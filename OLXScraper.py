import requests
import json
import csv
from datetime import datetime
from time import sleep
from lxml import html


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}


def links_scraper():
    estate_urls = []
    base_url = "https://www.olx.ba/artikal/"
    s = requests.Session()
    s.headers.update(headers)
    for category in range(23, 31):
        for estate_type in range(2):
            r = s.get("https://www.olx.ba/ajax/nekretnine_pretraga"
                      "?lat1=42.202479983125684&lat2=45.45088297676916&lng1=12.968261986970903&lng2=22.855957299470905"
                      "&kategorija=" + str(category) +
                      "&vrsta=" + str(estate_type) +
                      "&od=&do="
                      "&kvadrata_od=&kvadrata_do=")
            json_file = json.loads(r.text)
            for element in json_file['artikli']:
                estate_urls.append(base_url + element['id'])

    unique_estate_urls = list(set(estate_urls))
    open("links_" + datetime.today().strftime('%Y_%m_%d') + ".txt", "w").write('\n'.join(unique_estate_urls) + '\n')


csv_header = ["Address", "Alarm", "Balcony", "Pool", "ArmoredDoor", "NumberOfQuestions", "NumberOfViews",
              "NumberOfPhotos", "NumberOfRooms", "NumberOfFloors", "PriceBefore1", "PriceBeforeDate1", "PriceBefore2",
              "PriceBeforeDate2", "PostingDate", "Garage", "BuildingDate", "BuildingPermit",
              "Internet", "Rented", "CableTV", "Sewerage", "VehicleCapacity", "Category", "AirConditioning", "Kitchen",
              "Size", "BalconySize", "Latitude", "Elevator", "Location", "Longitude", "StorageRoom", "Furnished",
              "RecentlyAdapted", "NewBuilding", "Garden", "OLX ID", "KeepingRoom", "Parking", "Gas", "BasementAttic",
              "Entrance", "PrimaryOrientation", "Sold", "Floor", "State", "Electricity", "Telephone",
              "UtilitiesIncluded", "LegalPapers", "UrbanPermit", "Url", "VideoSurveillance", "Water", "GarageType",
              "HeatingType", "ObjectType", "AdType", "FlooringType", "ToiletBathroom", "ForStudents", "ScrapingDate",
              "Price"]
urls = []
while True:
    try:
        urls = open(r"links\links_all.txt").read().splitlines()
        break
    except FileNotFoundError:
        links_scraper()
        urls = open("links_" + datetime.today().strftime('%Y_%m_%d') + ".txt").read().splitlines()
        break

csv_file = open("data_all.csv", mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file, dialect=csv.excel)
csv_writer.writerow(csv_header)
csv_file.flush()
for num, url in enumerate(urls):
    s = requests.Session()
    s.headers.update(headers)
    while True:
        try:
            r = s.get(url)
            if r.status_code == 404:
                print("Page with url" + url + " could not be found.")
                break
            if r.status_code != 200:
                sleep(5)
                print("Response code is not success, but was " + r.status_code)
                print("Sending request again")
                continue
            break
        except BaseException:
            sleep(1)
            print("An exception has occurred while requesting " + url)
            print("Trying again!")
            continue
    if r.status_code == 404:
        a = 5
        # need to save as row in csv with column deleted date and continue
    tree = html.fromstring(r.text)

    try:
        adresa = tree.xpath(".//div[text()='Adresa']/following-sibling::div")[0].text.strip()
    except:
        adresa = "N/A"
    try:
        tree.xpath(".//div[text()='Alarm']/following-sibling::div")[0]
        alarm = "1"
    except:
        alarm = "0"
    try:
        tree.xpath(".//div[text()='Balkon']/following-sibling::div")[0]
        balkon = "1"
    except:
        balkon = "0"
    try:
        tree.xpath(".//div[text()='Bazen']/following-sibling::div")[0]
        bazen = "1"
    except:
        bazen = "0"
    try:
        tree.xpath(".//div[text()='Blindirana vrata']/following-sibling::div")[0]
        blindirana_vrata = "1"
    except:
        blindirana_vrata = "0"
    try:
        broj_pitanja = tree.xpath(".//a[@id='pitanja_btn']/span")[0].text_content().strip()
    except:
        broj_pitanja = "N/A"
    try:
        broj_pregleda = tree.xpath(".//div[contains(text(),'Broj pregleda')]/following-sibling::div")[0].text.strip()
    except:
        broj_pregleda = "N/A"
    try:
        broj_slika = tree.xpath(".//a[contains(text(), 'SLIKE')]/span")[0].text_content().strip()
    except:
        broj_slika = "N/A"
    try:
        broj_soba = tree.xpath(".//div[text()='Broj soba']/following-sibling::div")[0].text.strip()
    except:
        broj_soba = "N/A"
    try:
        broj_spratova = tree.xpath(".//div[text()='Broj spratova']/following-sibling::div")[0].text.strip()
    except:
        broj_spratova = "N/A"
    try:
        cijena_prije_1 = tree.xpath(".//div[@class='op pop mobile-cijena ']")[0].attrib['data-content'].split('br>')[1].split('-')[0].strip()
    except:
        cijena_prije_1 = "N/A"
    try:
        datum_cijene_prije_1 = tree.xpath(".//div[@class='op pop mobile-cijena ']")[0].attrib['data-content'].split('br>')[1].split('>')[1].split('<')[0].strip()
    except:
        datum_cijene_prije_1 = "N/A"
    try:
        cijena_prije_2 = tree.xpath(".//div[@class='op pop mobile-cijena ']")[0].attrib['data-content'].split('-')[0].strip()
        if cijena_prije_2 == 'Nije bilo promjena cijene':
            cijena_prije_2 = "N/A"
    except:
        cijena_prije_2 = "N/A"
    try:
        datum_cijene_prije_2 = tree.xpath(".//div[@class='op pop mobile-cijena ']")[0].attrib['data-content'].split('>')[1].split('<')[0].strip()
    except:
        datum_cijene_prije_2 = "N/A"
    try:
        datum_objave = tree.xpath(".//div[contains(text(),'Datum objave')]/following-sibling::div/time")[0].text.strip()
    except:
        datum_objave = ""
    try:
        tree.xpath(".//div[text()='Garaža']/following-sibling::div")[0]
        garaza = "1"
    except:
        garaza = "0"
    try:
        godina_izgradnje = tree.xpath(".//div[text()='Godina izgradnje']/following-sibling::div")[0].text.strip()
    except:
        godina_izgradnje = ""
    try:
        tree.xpath(".//div[text()='Građevinska dozvola']/following-sibling::div")[0]
        gradjevinska_dozvola = "1"
    except:
        gradjevinska_dozvola = "0"
    try:
        tree.xpath(".//div[text()='Internet']/following-sibling::div")[0]
        internet = "1"
    except:
        internet = "0"
    try:
        tree.xpath(".//div[text()='Iznajmljeno']/following-sibling::div")[0]
        iznajmljeno = "1"
    except:
        iznajmljeno = "0"
    try:
        tree.xpath(".//div[text()='Kablovska TV']/following-sibling::div")[0]
        kablovska = "1"
    except:
        kablovska = "0"
    try:
        kanalizacija = tree.xpath(".//div[text()='Kanalizacija']/following-sibling::div")[0].text.strip()
    except:
        kanalizacija = "N/A"
    try:
        kapacitet_vozila = tree.xpath(".//div[text()='Kapacitet (vozila)']/following-sibling::div")[0].text.strip()
    except:
        kapacitet_vozila = "N/A"
    try:
        kategorija = tree.xpath(".//span[@itemprop='title']")[-1].text.strip()
    except:
        kategorija = "N/A"
    try:
        tree.xpath(".//div[text()='Klima']/following-sibling::div")[0]
        klima = "1"
    except:
        klima = "0"
    try:
        kuhinja = tree.xpath(".//div[text()='Kuhinja']/following-sibling::div")[0].text.strip()
    except:
        kuhinja = "N/A"
    try:
        kvadrata = tree.xpath(".//div[text()='Kvadrata']/following-sibling::div")[0].text.strip()
    except:
        kvadrata = "N/A"
    try:
        kvadratura_balkona = tree.xpath(".//div[text()='Kvadratura balkona']/following-sibling::div")[0].text.strip()
    except:
        kvadratura_balkona = "N/A"
    try:
        latitude = tree.xpath(".//script[contains(text(), 'LatLng')]")[0].text.split('LatLng(')[1].split(',')[0].strip()
    except:
        latitude = "N/A"
    try:
        tree.xpath(".//div[text()='Lift']/following-sibling::div")[0]
        lift = "1"
    except:
        lift = "0"
    try:
        lokacija = tree.xpath(".//div[@class='op pop mobile-lokacija']")[0].attrib["data-content"].strip()
    except:
        lokacija = "N/A"
    try:
        longitude = tree.xpath(".//script[contains(text(), 'LatLng')]")[0].text.split('LatLng(')[1].split(',')[1].split(')')[0].strip()
    except:
        longitude = "N/A"
    try:
        tree.xpath(".//div[text()='Magacin']/following-sibling::div")[0]
        magacin = "1"
    except:
        magacin = "0"
    try:
        namjesten = tree.xpath(".//div[text()='Namješten?']/following-sibling::div")[0].text.strip()
    except:
        namjesten = "N/A"
    try:
        tree.xpath(".//div[text()='Nedavno adaptirana']/following-sibling::div")[0]
        nedavno_adaptiran = "1"
    except:
        nedavno_adaptiran = "0"
    try:
        tree.xpath(".//div[text()='Novogradnja']/following-sibling::div")[0]
        novogradnja = "1"
    except:
        novogradnja = "0"
    try:
        okucnica = tree.xpath(".//div[text()='Okućnica (kvadratura)']/following-sibling::div")[0].text.strip()
    except:
        okucnica = "N/A"
    try:
        OLX_ID = tree.xpath(".//div[contains(text(),'OLX ID')]/following-sibling::div")[0].text.strip()
    except:

        OLX_ID = ""
    try:
        tree.xpath(".//div[text()='Ostava/špajz']/following-sibling::div")[0]
        ostava = "1"
    except:
        ostava = "0"
    try:
        tree.xpath(".//div[text()='Parking']/following-sibling::div")[0]
        parking = "1"
    except:
        parking = "0"
    try:
        tree.xpath(".//div[text()='Plin']/following-sibling::div")[0]
        plin = "1"
    except:
        plin = "0"
    try:
        tree.xpath(".//div[text()='Podrum/Tavan']/following-sibling::div")[0]
        podrum_tavan = "1"
    except:
        podrum_tavan  = "0"
    try:
        prilaz = tree.xpath(".//div[text()='Prilaz']/following-sibling::div")[0].text.strip()
    except:
        prilaz = "N/A"
    try:
        primarna_orjentacija = tree.xpath(".//div[text()='Primarna orjentacija']/following-sibling::div")[0].text.strip()
    except:
        primarna_orjentacija = "N/A"
    try:
        tree.xpath(".//div[@id='prodano']")[0]
        prodano = "1"
    except:
        prodano = "0"
    try:
        sprat = tree.xpath(".//div[text()='Sprat']/following-sibling::div")[0].text.strip()
    except:
        sprat = "N/A"
    try:
        stanje = tree.xpath(".//div[@class='op mobile-stanje']/p[2]")[0].text.strip()
    except:
        stanje = "N/A"
    try:
        tree.xpath(".//div[text()='Struja']/following-sibling::div")[0]
        struja = "1"
    except:
        struja = "0"
    try:
        tree.xpath(".//div[text()='Telefonski priključak']/following-sibling::div")[0]
        telefonski_prikljucak = "1"
    except:
        telefonski_prikljucak = "0"
    try:
        tree.xpath(".//div[text()='Uključen trošak režija']/following-sibling::div")[0]
        ukljucen_trosak_rezija = "1"
    except:
        ukljucen_trosak_rezija = "0"
    try:
        tree.xpath(".//div[contains(text(), 'Uknjiženo')]/following-sibling::div")[0]
        uknjizeno = "1"
    except:
        uknjizeno = "0"
    try:
        tree.xpath(".//div[text()='Urbanistička dozvola']/following-sibling::div")[0]
        urbanisticka_dozvola = "1"
    except:
        urbanisticka_dozvola = "0"
    try:
        tree.xpath(".//div[text()='Video nadzor']/following-sibling::div")[0]
        video_nadzor = "1"
    except:
        video_nadzor = "0"
    try:
        tree.xpath(".//div[text()='Voda']/following-sibling::div")[0]
        voda = "1"
    except:
        voda = "0"
    try:
        vrsta_garaze = tree.xpath(".//div[text()='Vrsta']/following-sibling::div")[0].text.strip()
    except:
        vrsta_garaze = "N/A"
    try:
        vrsta_grijanja = tree.xpath(".//div[text()='Vrsta grijanja']/following-sibling::div")[0].text.strip()
    except:
        vrsta_grijanja = "N/A"
    try:
        vrsta_objekta = tree.xpath(".//div[text()='Vrsta objekta']/following-sibling::div")[0].text.strip()
    except:
        vrsta_objekta = "N/A"
    try:
        vrsta_oglasa = tree.xpath(".//div[contains(text(),'Vrsta oglasa')]/following-sibling::div")[0].text.strip()
    except:
        vrsta_oglasa = "N/A"
    try:
        vrsta_poda = tree.xpath(".//div[text()='Vrsta poda']/following-sibling::div")[0].text.strip()
    except:
        vrsta_poda = "N/A"
    try:
        wc = tree.xpath(".//div[text()='WC / Kupatilo']/following-sibling::div")[0].text.strip()
    except:
        wc = "N/A"
    try:
        tree.xpath(".//div[text()='Za studente']/following-sibling::div")[0]
        za_studente = "1"
    except:
        za_studente = "0"
    scrape_datum = datetime.today().strftime('%Y_%m_%d')
    try:
        cijena = tree.xpath(".//div[@class='op pop mobile-cijena ']/p[2]")[0].text.replace('.', '').replace(',', '.').strip()
        if "Po dogovoru" in cijena:
            cijena = "N/A"
    except:
        cijena = "N/A"

    csv_writer.writerow([adresa, alarm, balkon, bazen, blindirana_vrata, broj_pitanja,
                         broj_pregleda, broj_slika, broj_soba, broj_spratova, cijena_prije_1,
                         datum_cijene_prije_1, cijena_prije_2, datum_cijene_prije_2, datum_objave,
                         garaza, godina_izgradnje, gradjevinska_dozvola, internet, iznajmljeno, kablovska, kanalizacija,
                         kapacitet_vozila, kategorija, klima, kuhinja, kvadrata,
                         kvadratura_balkona, latitude, lift, lokacija, longitude, magacin, namjesten, nedavno_adaptiran,
                         novogradnja, okucnica, OLX_ID, ostava, parking, plin, podrum_tavan, prilaz,
                         primarna_orjentacija, prodano, sprat, stanje, struja, telefonski_prikljucak,
                         ukljucen_trosak_rezija, uknjizeno, urbanisticka_dozvola, url,
                         video_nadzor, voda, vrsta_garaze, vrsta_grijanja, vrsta_objekta, vrsta_oglasa, vrsta_poda, wc,
                         za_studente, scrape_datum, cijena])
    csv_file.flush()
    print("Added: " + url, "Left: " + str(len(urls)-num), "Done: " + str(num))

csv_file.close()

