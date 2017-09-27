from datetime import date
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

    name = "gwinnettsmartweb"

    def start_requests(self):
        url = 'http://www.gwinnettcountysheriff.com/smartwebclient/'
        formdata = {
            'TypeSearch': self.SearchType.CurrentInmatesOnly,
            'SearchSortOption': self.SortType.BookingDate,
            'SearchOrderOption': self.SortOrder.Descending
        }

        yield scrapy.http.FormRequest(url=url, formdata=formdata, callback=self.parse)

    def parse(self, response):
        filename = 'inmate-roster-{0}.html'.format(date.today())
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)