
from urllib.parse import urlencode, quote_plus


def build_url(base_url, get_param_dic):
    return F'{base_url}?{urlencode(get_param_dic, quote_via=quote_plus)}'
