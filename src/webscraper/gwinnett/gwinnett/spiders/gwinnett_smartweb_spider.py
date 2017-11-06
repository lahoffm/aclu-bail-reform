import csv
import datetime
from gwinnett.items import GwinnettInmate, GwinnettInmateLoader
import scrapy


class GwinnettSmartWebSpider(scrapy.Spider):
    class SearchType:
        CurrentInmatesOnly = '0'
        ReleasedInmatesOnly = '1'
        CurrentAndReleasedInmates = '2'

    class SortType:
        Name = '0'
        BookingDate = '1'

    class SortOrder:
        Ascending = '0'
        Descending = '1'

    name = 'gwinnettsmartweb'

    SCRAPE_URL = 'http://www.gwinnettcountysheriff.com/smartwebclient/'
    SEARCH_FORMDATA = {
        'TypeSearch': SearchType.CurrentInmatesOnly,
        'SearchSortOption': SortType.BookingDate,
        'SearchOrderOption': SortOrder.Descending
    }

    def __init__(self):
        self.scrape_start_time = None

    def start_requests(self):
        self.scrape_start_time = datetime.datetime.now()

        yield scrapy.http.FormRequest(url=self.SCRAPE_URL, formdata=self.SEARCH_FORMDATA, callback=self.parse)

    def parse(self, response):
        inmate_rows = response.xpath("//table[@class='JailView']/tr")
        if len(inmate_rows) == 0:
            self.log('Error parsing search results -- no JailView table body found!')
            return

        current_inmate = None
        for row in inmate_rows:
            if row.extract().find('InmateRecordSeperater') > -1:
                continue
            elif len(row.xpath(".//table[@id='JailViewHolds']")) > 0:
                continue
            elif len(row.xpath(".//table[@id='JailViewCharges']")) > 0:
                charge_info = self.parse_charges(row.xpath(".//table[@id='JailViewCharges']").xpath(".//tr"))
                for charge in charge_info['charges']:
                    current_inmate.add_value('charges', charge)
                for severity in charge_info['severity']:
                    current_inmate.add_value('severity', severity)
            else:
                if current_inmate is not None:
                    yield current_inmate.load_item()
                current_inmate = self.create_inmate_from_row(row)

        if current_inmate is not None:
            yield current_inmate.load_item()

    def create_inmate_from_row(self, row):
        inmate = GwinnettInmateLoader(item=GwinnettInmate(), selector=row)

        inmate_header = row.xpath(".//td[@class='SearchHeader']/text()")
        if len(inmate_header) == 0:
            return None

        inmate_header_text = inmate_header[0].extract()
        (names, race, sex) = self.parse_inmate_header(inmate_header_text)
        inmate.add_value('inmate_firstname', names[0])
        inmate.add_value('inmate_lastname', names[1])
        inmate.add_value('inmate_race', race)
        inmate.add_value('inmate_sex', sex)

        inmate_info_loader = inmate.nested_xpath(".//tbody/tr")
        inmate_info_loader.add_xpath('inmate_age', get_cell_xpath('Age On Booking Date'))
        inmate_info_loader.add_xpath('inmate_address', get_cell_xpath('Address Given'))
        inmate_info_loader.add_xpath('processing_numbers', get_cell_xpath('Booking No'))
        inmate_info_loader.add_xpath('facility', get_cell_xpath('CELL Assigned'))
        inmate_info_loader.add_xpath('bond_amount', get_cell_xpath('Bond Amount'))

        # Since 'Age On Booking Date'/'Booking Date' and 'Visitation Status'/'Status' are both
        # matched by the basic contains XPath, we have to be more specific to get the true cell.
        inmate_info_loader.add_xpath('booking_timestamp', get_re_cell_xpath('Booking Date'))
        inmate_info_loader.add_xpath('current_status', get_re_cell_xpath('Status'))

        inmate.add_value('county_name', 'gwinnett')
        inmate.add_value('timestamp', self.scrape_start_time)
        inmate.add_value('url', 'http://www.gwinnettcountysheriff.com/smartwebclient/')

        return inmate

    def parse_inmate_header(self, header):
        race_index = header.find('(')
        sex_index = header.find('/', race_index)

        name = header[:race_index].strip()
        name_divider_index = name.find(',')
        first_name = name[name_divider_index + 1:]
        last_name = name[:name_divider_index]
        names = [first_name, last_name]

        race = header[race_index + 1:sex_index]
        sex = header[sex_index + 1:header.find(')', sex_index)]
        return names, race, sex

    def parse_charges(self, charge_rows):
        charges = []
        severities = []
        for row in charge_rows:
            if row.extract().find('SearchHeader') > -1:
                continue
            elif len(row.xpath(".//td[contains(., '[+]')]")) > 0:
                charge, severity = self.parse_charge(row)
                charges.append(charge)
                severities.append(severity)
            else:
                charges[-1] = row.xpath('.//td/text()').extract_first()
        return {'charges': charges, 'severity': severities}

    def parse_charge(self, charge_row):
        charge = charge_row.xpath('.//td/following-sibling::*[1]/text()').extract_first().strip()
        statute = charge_row.xpath('.//td/following-sibling::*[3]/text()').extract_first().strip()
        severity = charge_row.xpath('.//td/following-sibling::*[5]/text()').extract_first().strip()
        return statute + ' ' + charge, severity

    def write_file(self, inmate_records):
        filename = 'gwinnett_{0}.csv'.format(self.scrape_start_time.strftime('%Y_%m_%d_%H_%M_%S'))
        with open(filename, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(get_field_names_csv())
            for record in inmate_records:
                writer.writerow(record.get_field_values_csv())
        self.log('Saved file %s' % filename)


def get_cell_xpath(cell_title):
    return ".//td[contains(., '" + cell_title + "')]/following-sibling::*[1]/text()"

def get_re_cell_xpath(cell_title):
    return ".//td[re:test(., '^\s*" + cell_title + "')]/following-sibling::*[1]/text()"
