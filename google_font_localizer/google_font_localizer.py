import requests
import re
from argparse import ArgumentParser

import attr
import tinycss

regex_ampersand = '&(amp;)?'


@attr.s
class WebfontsHelperAPI:
    base_url = attr.ib(default='https://google-webfonts-helper.herokuapp.com/api/fonts', init=False)

    def get_font(self, subsets,):
        pass

    def parse_css(self):
        css_parser = tinycss.make_parser('fonts3')
        css = css_parser.parse_stylesheet(requests.get(self.base_url).text)

    def change_css(self):
        pass


@attr.s
class FontWeight:
    weight = attr.ib(converter=int, validator=attr.validators.instance_of(int))
    style = attr.ib(default=None)

    @classmethod
    def from_google_fonts_weight(cls, weight):
        return cls(*weight.partition('i')[:2])

    @property
    def webhelper_format(self):
        if self.style:
            return self.weight + 'italic'
        return self.weight


@attr.s
class GoogleWebFont:
    name = attr.ib()
    weights_list = attr.ib()
    weights = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.weights = [FontWeight.from_google_fonts_weight(weight) for weight in self.weights_list]

    # Web Fonts Helper expects some values to be slightly different
    @property
    def webfonts_helper_name(self):
        return self.name.replace('+', '-').lower()

    @property
    def webfonts_helper_weights(self):
        return [weight.webhelper_format for weight in self.weights]

    # Css name
    @property
    def css_name(self):
        return self.name.replace('+', ' ')




@attr.s
class GoogleWebFontList:
    fonts = attr.ib(validator=attr.validators.instance_of(list))
    subsets = attr.ib(validator=attr.validators.instance_of(list))

    @classmethod
    def from_google_font_url(cls, url):
        fonts = []
        font_parts = re.search('family=(.*)', url).group(1).split('|')

        # Get the subsets from the last font_parts element, remove this query part from element afterwards
        subsets = re.search('subset=(.*)', font_parts[-1]).group(1).split(',')
        font_parts[-1] = re.sub('{re_amp}subset=.*'.format(re_amp=regex_ampersand), '', font_parts[-1])

        for font_part in font_parts:
            # First match is the font name, the rest is font weights
            parts = re.findall('[-+\w]+', string=font_part)
            print('%s -> %s' % (font_part, parts))
            fonts.append(
                GoogleWebFont(
                    name=parts[0],
                    weights_list=parts[1:]
                )
            )
        return cls(fonts=fonts, subsets=subsets)


@attr.s
class FontLocalizer:
    font_url = attr.ib()
    font_list = attr.ib(validator=attr.validators.instance_of(GoogleWebFontList))
    webfonts_helper = attr.ib(init=False, factory=WebfontsHelperAPI)


def parse_args():
    parser = ArgumentParser(description="Localize Google Fonts + CSS")
    parser.add_argument("url", metavar="URL", help="The URL Google Fonts requires you to include")

    args = parser.parse_args(
        ['https://fonts.googleapis.com/css?family=Lato:400,700i|Merriweather|Open+Sans:300i,400&amp;subset=cyrillic-ext,vietnamese']
    )

    return args.url


url = parse_args()


localizer = FontLocalizer(
    font_url=url,
    font_list=GoogleWebFontList.from_google_font_url(url)
)

print(localizer)


