# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import requests



SEMRUSH_API_URL = 'http://api.semrush.com/'
SEMRUSH_ASNS_API_URL = 'http://api.asns.backend.semrush.com/'
SEMRUSH_API_V1_URL = 'http://api.semrush.com/analytics/v1/'
SEMRUSH_API_V3_URL = 'https://api.semrush.com/analytics/ta/api/v3/'

REGIONAL_DATABASES = {
    'google.com': 'us',
    'google.co.uk': 'uk',
    'google.ca': 'ca',
    'google.ru': 'ru',
    'google.de': 'de',
    'google.fr': 'fr',
    'google.es': 'es',
    'google.it': 'it',
    'google.com.br': 'br',
    'google.com.au': 'au',
    'bing.com': 'bing-us',
    'google.com.ar': 'ar',
    'google.be': 'be',
    'google.ch': 'ch',
    'google.dk': 'dk',
    'google.fi': 'fi',
    'google.com.hk': 'hk',
    'google.ie': 'ie',
    'google.co.il': 'il',
    'google.com.mx': 'mx',
    'google.nl': 'nl',
    'google.no': 'no',
    'google.pl': 'pl',
    'google.se': 'se',
    'google.com.sg': 'sg',
    'google.com.tr': 'tr',
    'm.google.com': 'mobile-us',
    'google.co.jp': 'jp',
    'google.co.in': 'in'
}


class SemrushClient(object):

    def __init__(self, key):
        if not key:
            raise Exception('A Semrush key must be provided')

        self.api_url = SEMRUSH_API_URL
        self.key = key

    @staticmethod
    def get_database_from_search_engine(search_engine='google.com'):
        if search_engine in REGIONAL_DATABASES:
            return REGIONAL_DATABASES[search_engine]
        else:
            raise Exception('%s - is not an accepted search engine.' % search_engine)

    # Report producing methods
    def produce(self, report_type, **kwargs):
        data = self.retrieve(report_type, **kwargs)
        return self.parse_response(data)

    def retrieve(self, report_type, **kwargs):
        kwargs['type'] = report_type
        kwargs['key'] = self.key

        response = requests.get(self.api_url, params=kwargs)

        if response.status_code == 200:
            return response.content
        else:
            raise Exception(response.content)

    @staticmethod
    def parse_response(data):
        results = []
        data = data.decode('unicode_escape')
        lines = data.split('\r\n')
        lines = list(filter(bool, lines))
        columns = lines[0].split(';')

        for line in lines[1:]:
            result = {}
            for i, datum in enumerate(line.split(';')):
                result[columns[i]] = datum.strip('"\n\r\t')
            results.append(result)

        return results

    # Overview Reports
    def domain_ranks(self, domain, **kwargs):
        """
        Domain Overview (All Databases)
        This report provides live or historical data on a domain's keyword rankings in both organic and paid search in
        all regional databases.
        https://pt.semrush.com/api-analytics/#domain_ranks
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - display_date: date in format "YYYYMM15"
        - export_columns: Db, Dt, Dn, Rk, Or, Ot, Oc, Ad, At, Ac, Sh, Sv, FKn, FPn
        - database: default global
        - display_limit: integer, default 10000
        - display_offset: integer
        """
        return self.produce('domain_ranks', domain=domain, **kwargs)

    def domain_rank(self, domain, database, **kwargs):
        """
        Domain Overview (One Database)
        This report provides live or historical data on a domain's keyword rankings in both organic and paid search in a
        chosen regional database.
        https://pt.semrush.com/api-analytics/#domain_rank
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - export_escape: 1 to wrap report columns in quotation marks (")
        - export decode: 1 or 0, 0 to url encode string
        - display_date: date in format "YYYYMM15"
        - export_columns: Dn, Rk, Or, Xn, Ot, Oc, Ad, At, Ac, FKn, FPn
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_rank', domain=domain, database=database, **kwargs)

    def domain_rank_history(self, domain, database, **kwargs):
        """
        Domain Overview (History)
        This report provides live and historical data on a domain's keyword rankings in both organic and paid search in
        a chosen database.
        https://pt.semrush.com/api-analytics/#domain_rank_history
        
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_daily: 1
        - export_columns: Rk, Or, Xn, Ot, Oc, Ad, At, Ac, Dt, FKn, FPn
        - display_sort: dt_asc, dt_desc
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_rank_history', domain=domain, database=database, **kwargs)

    def rank_difference(self, database, **kwargs):
        """
        Winners and Losers
        This report shows changes in the number of keywords, traffic, and budget estimates of the most popular websites
        in Google's top 20 and paid search results.
        https://pt.semrush.com/api-analytics/#domain_rank_history
        
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Dn, Rk, Or, Ot, Oc, Ad, At, Ac, Om, Tm, Um, Am, Bm, Cm
        - display_sort: om_asc, om_desc, tm_asc, tm_desc, um_asc, um_desc, am_asc, am_desc, bm_asc, bm_desc, cm_asc,
            cm_desc
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('rank_difference', database=database, **kwargs)

    def rank(self, database, **kwargs):
        """
        Semrush Rank
        This report lists the most popular domains ranked by traffic originating from Google's top 20 organic search
        results.
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Dn, Rk, Or, Ot, Oc, Ad, At, Ac
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('rank', database=database, **kwargs)

    # Domain Reports
    def domain_organic(self, domain, database, **kwargs):
        """
        Domain Organic Search Keywords
        This report lists keywords that bring users to a domain via Google's top 20 organic search results.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Ph, Po, Pp, Pd, Nq, Cp, Ur, Tr, Tc, Co, Nr, Td
        - display_sort: tr_asc, tr_desc, po_asc, po_desc, tc_asc, tc_desc
        - display_positions: new, lost, rise or fall
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_organic', domain=domain, database=database, **kwargs)

    def domain_adwords(self, domain, database, **kwargs):
        """
        Domain Paid Search
        This report lists keywords that bring users to a domain via Google's paid search results.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Ph, Po, Pp, Pd, Ab, Nq, Cp, Tr, Tc, Co, Nr, Td, Tt, Ds, Vu, Ur
        - display_sort: tr_asc, tr_desc, po_asc, po_desc, tc_asc, tc_desc
        - display_positions: new, lost, rise or fall
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_adwords', domain=domain, database=database, **kwargs)

    def domain_adwords_unique(self, domain, database, **kwargs):
        """
        Ads Copies
        This report shows unique ad copies SEMrush noticed when the domain ranked in Google's paid search results for
        keywords from our databases.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Ph, Po, Pp, Nq, Cp, Tr, Tc, Co, Nr, Td, Tt, Ds, Vu, Ur, Pc
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_adwords_unique', domain=domain, database=database, **kwargs)

    def domain_organic_organic(self, domain, database, **kwargs):
        """
        Competitors In Organic Search
        This report lists a domain's competitors in organic search results.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Dn, Cr, Np, Or, Ot, Oc, Ad
        - display_sort: np_desc, cr_desc
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_organic_organic', domain=domain, database=database, **kwargs)

    def domain_adwords_adwords(self, domain, database, **kwargs):
        """
        Competitors In Paid Search
        This report lists a domain's competitors in paid search results.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Dn, Cr, Np, Ad, At, Ac, Or
        - display_sort: np_desc, cr_desc
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_adwords_adwords', domain=domain, database=database, **kwargs)

    def domain_adwords_historical(self, domain, database, **kwargs):
        """
        Domains Ads History
        This report shows keywords a domain has bid on in the last 12 months and its positions in paid search results.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Ph, Dt, Po, Cp, Nq, Tr, Ur, Tt, Ds, Vu, Cv
        - display_sort: cv_asc, cv_desc
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_adwords_historical', domain=domain, database=database, **kwargs)

    def domain_domains(self, domains, database, **kwargs):
        """
        Domain Vs. Domain
        This report allows users to compare up to five domains by common keywords, unique keywords, all keywords, or
        search terms that are unique to the first domain.
        :param domains: The domains to query data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Ph, P0, P1, P2, P3, P4, Nr, Cp, Co, Nq
        - display_sort: p0_asc, p0_desc, p1_asc, p1_desc, p2_asc, p2_desc, p3_asc, p3_desc, p4_asc, p4_desc, nq_asc,
            nq_desc, co_asc, co_desc, cp_asc, cp_desc, nr_asc, nr_desc
        - display_filter:
        Note: Refer to SEMrush API documentation for format of domains
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_domains', domains=domains, database=database, **kwargs)

    def domain_shopping(self, domain, database, **kwargs):
        """
        Domain PLA Search Keywords
        This report lists keywords that trigger a domain's product listing ads to appear in Google's paid search
        results.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Ph, Po, Pp, Pd, Ab, Nq, Cp, Tr, Tc, Co, Nr, Td, Tt, Ds, Vu, Ur
        - display_sort: tr_asc, tr_desc, po_asc, po_desc, tc_asc, tc_desc
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_shopping', domain=domain, database=database, **kwargs)

    def domain_shopping_unique(self, domain, database, **kwargs):
        """
        PLA Copies
        This report shows product listing ad copies SEMrush noticed when the domain ranked in Google's paid search results
        for keywords from our databases.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Ph, Po, Pp, Nq, Cp, Tr, Tc, Co, Nr, Td, Tt, Ds, Vu, Ur, Pc
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_shopping_unique', domain=domain, database=database, **kwargs)

    def domain_shopping_shopping(self, domain, database, **kwargs):
        """
        PLA Competitors
        This report lists domains a queried domain is competing against in Google's paid search results with product
        listing ads.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Dn, Cr, Np, Ad, At, Ac, Or
        - display_sort: np_asc, np_desc, cr_asc, cr_desc
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_shopping_shopping', domain=domain, database=database, **kwargs)
    
    def domain_organic_unique(self, domain, database, **kwargs):
        """
        This report shows unique pages of the analyzed domain ranking in Google's top 100 results organic search results.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Ur, Pc, Tg, Tr
        - display_sort: Pc, Tg, Tr
        - display_filter: Ur, Pc, Tg, Tr
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_organic_unique', domain=domain, database=database, **kwargs)
    
    def domain_organic_subdomains(self, domain, database, **kwargs):
        """
        This report shows subdomains of the analyzed domain ranking in Google's top 100 organic search results.
        :param domain: The domain to query data for ie. 'example.com'
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Ur, Pc, Tg, Tr
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('domain_organic_subdomains', domain=domain, database=database, **kwargs)

    # Keyword Reports
    def phrase_all(self, phrase, **kwargs):
        """
        Keyword Overview (All Databases)
        This report provides a summary of a keyword, including its volume, CPC, competition, and the number of results
        in all regional databases.
        :param phrase: The phrase or term to obtain data for
        Optional kwargs
        - database:
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Db, Ph, Nq, Cp, Co
        """
        return self.produce('phrase_all', phrase=phrase, **kwargs)

    def phrase_this(self, phrase, database, **kwargs):
        """
        Keyword Overview (One Database)
        This report provides a summary of a keyword, including its volume, CPC, competition, and the number of results
        in a chosen regional database.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Ph, Nq, Cp, Co, Nr
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_this', phrase=phrase, database=database, **kwargs)
    
    def phrase_these(self, phrase, database, **kwargs):
        """
        This report provides a summary of up to 100 keywords, including its volume, 
        CPC, competition, and the number of results in a chosen regional database.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Ph, Nq, Cp, Co, Nr, Td
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_these', phrase=phrase, database=database, **kwargs)   

    def phrase_organic(self, phrase, database, **kwargs):
        """
        Organic Results
        This report lists domains that are ranking in Google's top 20 organic search results with a requested keyword.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Dn, Ur
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_organic', phrase=phrase, database=database, **kwargs)

    def phrase_adwords(self, phrase, database, **kwargs):
        """
        Paid Results
        This report lists domains that are ranking in Google's paid search results with a requested keyword.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Dn, Ur
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_adwords', phrase=phrase, database=database, **kwargs)

    def phrase_related(self, phrase, database, **kwargs):
        """
        Related Keywords
        This report provides an extended list of related keywords, synonyms, and variations relevant to a queried term
        in a chosen database.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Ph, Nq, Cp, Co, Nr, Td
        - display_sort: nq_asc, nq_desc, cp_asc, cp_desc, co_asc, co_desc, nr_asc, nr_desc
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_related', phrase=phrase, database=database, **kwargs)

    def phrase_adwords_historical(self, phrase, database, **kwargs):
        """
        Keywords Ads History
        This report shows domains that have bid on a requested keyword in the last 12 months and their positions in paid
        search results.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Dn, Dt, Po, Ur, Tt, Ds, Vu, At, Ac, Ad
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_adwords_historical', database=database, **kwargs)

    def phrase_fullsearch(self, phrase, database, **kwargs):
        """
        Phrase Match Keywords
        The report offers a list of phrase matches and alternate search queries, including particular keywords or
        keyword expressions.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Ph, Nq, Cp, Co, Nr, Td
        - display_sort: nq_asc, nq_desc, cp_asc, cp_desc, co_asc, co_desc, nr_asc, nr_desc
        - display_filter:
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_fullsearch', phrase=phrase, database=database, **kwargs)
    
    def phrase_questions(self, phrase, database, **kwargs):
        """
        The report provides a list of phrase questions relevant to a queried term in a chosen database.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: Ph, Nq, Cp, Co, Nr, Td
        - display_sort: nq_asc, nq_desc, cp_asc, cp_desc, co_asc, co_desc, nr_asc, nr_desc
        - display_filter: Ph, Nq, Cp, Co, Nr
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_questions', phrase=phrase, database=database, **kwargs)

    def phrase_kdi(self, phrase, database, **kwargs):
        """
        Keyword Difficulty
        This report provides keyword difficulty, an index that helps to estimate how difficult it would be to seize
        competitors' positions in organic search within the Google's top 20 with an indicated search term.
        :param phrase: The phrase or term to obtain data for
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - export_escape: 1
        - export_columns: Ph, Kd
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('phrase_kdi', phrase=phrase, database=database, **kwargs)

    # URL Reports
    def url_organic(self, url, database, **kwargs):
        """
        URL Organic Search Keywords
        This report lists keywords that bring users to a URL via Google's top 20 organic search results.
        :param url: The URL to obtain data for, ie. http://example.com
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Ph, Po, Nq, Cp, Co, Tr, Tc, Nr, Td
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('url_organic', url=url, database=database, **kwargs)

    def url_adwords(self, url, database, **kwargs):
        """
        URL Paid Search Keywords
        This report lists keywords that bring users to a URL via Google's paid search results.
        :param url: The URL to obtain data for, ie. http://example.com
        :param database: The database to query, one of the choices from REGIONAL_DATABASES
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - display_date: date in format "YYYYMM15"
        - export_columns: Ph, Po, Nq, Cp, Co, Tr, Tc, Nr, Td, Tt, Ds
        """
        if database not in REGIONAL_DATABASES.values():
            raise Exception('%s - is not an accepted database.' % database)
        return self.produce('url_adwords', url=url, database=database, **kwargs)

    # Display Advertising Reports
    def publisher_text_ads(self, domain, **kwargs):
        """
        Publisher Display Ads
        This report lists display ads that have appeared on a publisher's website.
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: title, text, first_seen, last_seen, times_seen, avg_position, media_type, visible_url
        - display_sort: last_seen_asc, last_seen_desc, first_seen_asc, first_seen_desc, times_seen_asc, times_seen_asc,
            times_seen_desc
        - device_type: all, desktop, smartphone_apple, smartphone_android, tablet_apple, tablet_android
        - display_filter:
        """
        kwargs['action'] = 'report'
        kwargs['export'] = 'api'
        self.api_url = SEMRUSH_ASNS_API_URL
        return self.produce('publisher_text_ads', domain=domain, **kwargs)

    def publisher_advertisers(self, domain, **kwargs):
        """
        Advertisers
        This report lists advertisers whose display ads have appeared on a queried publisher's website.
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: domain, ads_count, first_seen, last_seen, times_seen, ads_percent
        - display_sort: last_seen_asc, last_seen_desc, first_seen_asc, first_seen_desc, times_seen_asc, times_seen_desc
            ads_count_asc, ads_count_desc
        - device_type: all, desktop, smartphone_apple, smartphone_android, tablet_apple, tablet_android
        - display_filter:
        """
        kwargs['action'] = 'report'
        kwargs['export'] = 'api'
        self.api_url = SEMRUSH_ASNS_API_URL
        return self.produce('publisher_advertisers', domain=domain, **kwargs)

    def advertiser_publishers(self, domain, **kwargs):
        """
        Publishers
        This report lists publisher's websites where an advertiser's display ads have appeared.
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: domain, ads_count, first_seen, last_seen, times_seen, ads_percent
        - display_sort: last_seen_asc, last_seen_desc, first_seen_asc, first_seen_desc, times_seen_asc, times_seen_desc
            ads_count_asc, ads_count_desc
        - device_type: all, desktop, smartphone_apple, smartphone_android, tablet_apple, tablet_android
        - display_filter:
        """
        kwargs['action'] = 'report'
        kwargs['export'] = 'api'
        self.api_url = SEMRUSH_ASNS_API_URL
        return self.produce('advertiser_publishers', domain=domain, **kwargs)

    def advertiser_text_ads(self, domain, **kwargs):
        """
        Advertiser Display Ads
        This report lists display ads of a queried advertiser's website.
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: title,text, first_seen, last_seen, times_seen, avg_position, media_type, visible_url
        - display_sort: last_seen_asc, last_seen_desc, first_seen_asc, first_seen_desc, times_seen_asc, times_seen_asc,
            times_seen_desc
        - device_type: all, desktop, smartphone_apple, smartphone_android, tablet_apple, tablet_android
        - display_filter:
        """
        kwargs['action'] = 'report'
        kwargs['export'] = 'api'
        self.api_url = SEMRUSH_ASNS_API_URL
        return self.produce('advertiser_text_ads', domain=domain, **kwargs)

    def advertiser_landings(self, domain, **kwargs):
        """
        Landing Pages
        This report lists URLs of a domain's landing pages promoted via display ads.
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: target_url, first_seen, last_seen, times_seen, ads_count
        - display_sort: ast_seen_asc, last_seen_desc, first_seen_asc, first_seen_desc, times_seen_asc, times_seen_desc,
            ads_count_asc, ads_count_desc
        - device_type: all, desktop, smartphone_apple, smartphone_android, tablet_apple, tablet_android
        - display_filter:
        """
        kwargs['action'] = 'report'
        kwargs['export'] = 'api'
        self.api_url = SEMRUSH_ASNS_API_URL
        return self.produce('advertiser_landings', domain=domain, **kwargs)

    def advertiser_publisher_text_ads(self, domain, **kwargs):
        """
        Advertiser Display Ads On A Publishers Website
        This report lists the display ads of a given advertiser that have appeared on a particular publisher's website.
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_escape: 1
        - export_decode: 1 or 0
        - export_columns: title,text, first_seen, last_seen, times_seen, avg_position, media_type, visible_url
        - display_sort	last_seen_asc, last_seen_desc, first_seen_asc, first_seen_desc, times_seen_asc, times_seen_asc,
            times_seen_desc
        - device_type: all, desktop, smartphone_apple, smartphone_android, tablet_apple, tablet_android
        - display_filter:
        """
        kwargs['action'] = 'report'
        kwargs['export'] = 'api'
        self.api_url = SEMRUSH_ASNS_API_URL
        return self.produce('advertiser_publisher_text_ads', domain=domain, **kwargs)

    def advertiser_rank(self, domain, **kwargs):
        """
        Advertisers Rank
        This report lists advertisers ranked by the total number of display ads noticed by SEMrush.
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - export_escape: 1
        - export_columns: domain, ads_overall, text_ads_overall, ads_count, text_ads_count, times_seen, first_seen,
            last_seen, media_ads_overall, media_ads_count, publishers_overall, publishers_count
        - device_type: all, desktop, smartphone_apple, smartphone_android, tablet_apple, tablet_android
        """
        kwargs['action'] = 'report'
        kwargs['export'] = 'api'
        self.api_url = SEMRUSH_ASNS_API_URL
        return self.produce('advertiser_rank', domain=domain, **kwargs)

    def publisher_rank(self, domain, **kwargs):
        """
        Publishers Rank
        This report lists publishers ranked by the total number of display ads noticed by SEMrush.
        :param domain: The domain to query data for ie. 'example.com'
        Optional kwargs
        - export_escape: 1
        - export_columns: domain, ads_overall, text_ads_overall, ads_count, text_ads_count, times_seen, first_seen,
            last_seen, media_ads_overall, media_ads_count, advertiser_overall, advertiser_count
        - device_type: all, desktop, smartphone_apple, smartphone_android, tablet_apple, tablet_android
        """
        kwargs['action'] = 'report'
        kwargs['export'] = 'api'
        self.api_url = SEMRUSH_ASNS_API_URL
        return self.produce('publisher_rank', domain=domain, **kwargs)

    # Backlinks
    def backlinks_overview(self, target, target_type='root_domain'):
        """
        Backlinks Overview
        This report provides a summary of backlinks, including their type, referring domains and IP addresses for a
        domain, root domain, or URL.
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        Kwargs
        - target_type: domain, root_domain or url
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_overview', target=target, target_type=target_type)

    def backlinks(self, target, target_type='root_domain', **kwargs):
        """
        Backlinks
        This report lists backlinks for a domain, root domain, or URL.
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_columns: page_score, response_code, source_size, external_num, internal_num, redirect_url, source_url,
            source_title, image_url, target_url, target_title, anchor, image_alt, last_seen, first_seen, nofollow, form,
            frame, image, sitewide
        - display_sort: last_seen_asc, last_seen_desc, first_seen_asc, first_seen_desc
        - display_filter:
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks', target=target, target_type=target_type, **kwargs)

    def backlinks_refdomains(self, target, target_type='root_domain', **kwargs):
        """
        Referring Domains
        This report lists domains pointing to the queried domain, root domain, or URL.
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_columns: domain_score, domain, backlinks_num, ip, country, first_seen, last_seen
        - display_sort: rank_asc, rank_desc, backlinks_asc, backlinks_desc, last_seen_asc, last_seen_desc, first_seen_asc,
            first_seen_desc
        - display_filter:
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_refdomains', target=target, target_type=target_type, **kwargs)

    def backlinks_refips(self, target, target_type='root_domain', **kwargs):
        """
        Referring IPs
        This report lists IP addresses where backlinks to a domain, root domain, or URL are coming from.
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        - export_columns: ip, country, domains_num, backlinks_num, first_seen, last_seen
        - display_sort: backlinks_num_asc, backlinks_num_desc, last_seen_asc, last_seen_desc, first_seen_asc,
            first_seen_desc, domains_num_asc domains_num_desc
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_refips', target=target, target_type=target_type, **kwargs)

    def backlinks_tld(self, target, target_type='root_domain', **kwargs):
        """
        TLD Distribution
        This report shows referring domain distributions depending on their top-level domain type.
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        Optional kwargs
        - export_columns: zone, domains_num, backlinks_num
        - display_sort: backlinks_num_asc, backlinks_num_desc, domains_num_asc domains_num_desc
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_tld', target=target, target_type=target_type, **kwargs)

    def backlinks_geo(self, target, target_type='root_domain', **kwargs):
        """
        Referring Domains By Country
        This report shows referring domain distributions by country (an IP address defines a country).
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        Optional kwargs
        - export_columns: country, domains_num, backlinks_num
        - display_sort: backlinks_num_asc, backlinks_num_desc, domains_num_asc domains_num_desc
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_geo', target=target, target_type=target_type, **kwargs)

    def backlinks_anchors(self, target, target_type='root_domain', **kwargs):
        """
        Anchors
        This report lists anchor texts used in backlinks leading to the queried domain, root domain, or URL. It also
        includes the number of backlinks and referring domains per anchor.
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        Optional kwargs
        - export_columns: anchor, domains_num, backlinks_num, first_seen, last_seen
        - display_sort: backlinks_num_asc, backlinks_num_desc, last_seen_asc, last_seen_desc, first_seen_asc,
            first_seen_desc, domains_num_asc domains_num_desc
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_anchors', target=target, target_type=target_type, **kwargs)

    def backlinks_pages(self, target, target_type='root_domain', **kwargs):
        """
        Indexed Pages
        This report shows indexed pages of the queried domain
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        Optional kwargs
        - export_columns: response_code, backlinks_num, domains_num, last_seen, external_num, internal_num, source_url,
            source_title
        - display_sort: backlinks_num_asc, backlinks_num_desc, domains_num_asc, domains_num_desc, last_seen_asc,
            last_seen_desc
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_pages', target=target, target_type=target_type, **kwargs)
    
    def backlinks_competitors(self, target, target_type='root_domain', export_columns='ascore', **kwargs):
        """
        A list of domains with a similar backlink profile to the analyzed domain.
        :param target: An array of items, where an item is a root domain, domain or URL.
        :param target_type: An array of items, where an item is a type of 
            requested target specified in the parameter "targets[]".
        :param export_columns: ascore, neighbour, similarity, common_refdomains, domains_num, backlinks_num
        Optional kwargs
        - display_limit: integer
        - display-offset: integer
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_competitors', target=target, target_type=target_type, export_columns=export_columns, **kwargs)
    
    def backlinks_matrix(self, targets, target_types=['root_domain'], export_columns='domain', **kwargs):
        """
        This report shows how many backlinks are sent to you and your competitors from the same referring domains.
        :param targets: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_types: domain, root_domain or url
        :param export_columns: domain, domain_ascore, matches_num, backlinks_num
        Optional kwargs
        - display_sort: domain_ascore_desc, domain_ascore_asc, matchesnum_desc, matchesnum_asc, backlinksnum_0_desc, 
        backlinksnum_0_asc, backlinksnum_1_desc, backlinksnum_1_asc [...]
        - display_limit: integer
        - display_offset: integer
        - display_filter: backlinksnum_0, backlinksnum_1, backlinksnum_2, backlinksnum_3, backlinksnum_4, backlinksnum_5
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_matrix', targets=[targets], target_types=[target_types], export_columns=export_columns, **kwargs)
    
    def backlinks_comparison(self, target, target_type='root_domain', export_columns='target', **kwargs):
        """
        Compare your and your competitors' backlink profiles and link-building progress.
        :param targets: An array of items, where an item is a root domain, domain or URL. 
            The maximum number of targets is limited to 200.
        :param target_types: An array of items, where an item is a type of requested target 
            specified in the parameter "targets[]".
        :param export_columns: target, target_type, ascore, backlinks_num, domains_num, ips_num, follows_num, 
            nofollows_num,texts_num, images_num, forms_num, frames_num
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_comparison', targets=[targets], target_types=[target_types], export_columns=export_columns, **kwargs)
    
    def backlinks_ascore_profile(self, target, target_type='root_domain', **kwargs):
        """
        This report returns distribution of referring domains by Authority Score. When you run a query for a domain,
        in return, for each Authority Score value [from 0 to 100], you receive a number of domains that have at least
        one link, pointing to queried domain.
        :param target: Must be a root domain.
        :param target_type: Must be root_domain
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_ascore_profile', target=target, target_type=target_type, **kwargs)
    
    def backlinks_categories_profile(self, target, target_type='root_domain', export_columns='category_name', **kwargs):
        """
        This report returns the list of categories that referring domains belong to. When you run a query for a domain,
        in return, in each line, you receive a category and a number of domains that have at least one link, pointing to
        queried domain, that have such category. Results are sorted by a number of referring domains in descending order.
        This report is generated, based on the first 10,000 referring domains for given queried domain.
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        :param export_columns: category_name, rating
        Optional kwargs
        - display_limit: integer
        - display_offset: integer
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_categories_profile', target=target, target_type=target_type, **kwargs)
    
    def backlinks_categories(self, target, target_type='root_domain', **kwargs):
        """
        This report returns the list of categories queried domain belong to. When you run a query for a domain, 
        in return, in each line, you receive a category and a rating. Rating is a level of confidence that this 
        domain belongs to this category (ranged from 0 to 1). Results are sorted by the rating.
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_categories', target=target, target_type=target_type, **kwargs)

    def backlinks_historical(self, target, target_type='root_domain', export_columns='date', **kwargs):
        """
        This report returns only monthly historical trends of number of backlinks and referring domains for 
        queried domain. When you run a query for a domain, in return, in each line, you receive a date and a 
        number of backlinks and referring domains queried domain had on this date. Results are sorted by date 
        in descending order (from most recent to oldest).
        :param target: A domain, root domain, or URL address to retrieve the data for ie.
        :param target_type: domain, root_domain or url
        :param export_columns: date, backlinks_num, domains_num
        Optional kwargs
        - display_limit: integer
        """
        self.api_url = SEMRUSH_API_V1_URL
        return self.produce('backlinks_historical', target=target, target_type=target_type, export_columns=export_columns, **kwargs)
    
    
    #Traffic Analytics Reports - BETA
    def summary(self, targets, display_date='2021-10-01', device_type='desktop', country='PT', export_columns='display_date', **kwargs):
        """
        This report allows you to get the main estimated traffic metrics for multiple domains on a monthly basis 
        for desktop and mobile users in CSV format. To gain insights on your markets, prospects or partners, enter
        your target domain, use filters and get key traffic data: traffic rank, visits, unique visitors, pages per
        visit, avg. visit duration, and bounce rate.
        
        BETA 
        https://pt.semrush.com/api-analytics/#ta_summary
        
        :param targets: An array of both domains and subdomains separated by a comma. Required parameter. The maximum number of targets is limited to 200.
        :param display_date: The date in YYYY-MM-01 format. If the display_date parameter is not specified, data is shown for the previous month by default.
        :param device_type: desktop, mobile
        :param country
        :param export_columns
        """
        self.api_url = SEMRUSH_API_V3_URL + 'summary'
        return self.produce('backlinks_historical', targets=[targets], display_date=display_date, device_type=device_type, country=[country], export_columns=export_columns,**kwargs)
    
    

