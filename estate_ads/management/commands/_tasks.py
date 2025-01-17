from lxml import etree
from estate_ads.models import EstateAd, AdPicture
from estate_ads.utils import get_site


def read_ad_details(ad_id):
    ad = EstateAd.objects.get(pk=ad_id)

    # Now download ad
    if ad.link is None: return

    print "-- Detail: " + ad.link
    ad_html = get_site(ad.link)
    tree = etree.fromstring(ad_html, etree.HTMLParser())

    gallery_links = tree.xpath('//div[@id="galerija"]/a')
    for link in gallery_links:
        try:
            image = AdPicture(picture_url=link.attrib["href"])
            image.ad = ad
            image.save()
        except KeyError:    # Missing href
            continue

    ad.description = "\n".join(tree.xpath('//div[@class="web-opis"]//text()'))

    try:
        ad.administrative_unit = tree.xpath('//div[@class="main-data"]/table/tr')[3].getchildren()[1].text
    except IndexError:
        pass

    if ad.administrative_unit is None:
        ad.administrative_unit = ""

    try:
        ad.county = tree.xpath('//div[@class="main-data"]/table/tr')[4].getchildren()[1].text
    except IndexError:
        pass

    if ad.county is None:
        ad.county = ""

    ad.raw_detail_html = ad_html

    ad.save()