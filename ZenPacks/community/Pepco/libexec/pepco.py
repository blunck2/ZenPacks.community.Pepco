#!/usr/bin/env python

PREFIX="http://pepco.com/home/emergency/maps/stormcenter/data/data.xml?timestamp="

import time, urllib2
from lxml import etree

def download():
  nowMillis = int(time.time())
  url = PREFIX + str(nowMillis)

  u = urllib2.urlopen(url)
  xml = u.read()

  return xml


def scrub(original):
  clean = original.replace(' ', '_')
  clean = clean.replace("'", "")
  return clean


def summarize(xml):
  kv = {}
  tree = etree.XML(xml)

  r = tree.xpath('/root')[0]
  total_customers_out = r.findtext('total_customers')
  total_outages = r.findtext('total_outages')
  kv['total_customers_out'] = total_customers_out
  kv['total_outages'] = total_outages

  # collect areas
  r = tree.xpath('//areas')[0]

  total_customers = 0

  for area in r.iterchildren():
    name = scrub(area.findtext("area_name"))
    outages = area.findtext("custs_out")
    customers = area.findtext("total_custs")
    total_customers += int(customers)
  
    kv['%s_customers_out' % name] = outages
    kv['%s_total_customers' % name] = customers
  
  customers_out_percentage = (float(total_customers_out) / float(total_customers)) * 100

  kv['total_customers_out_as_percentage'] = customers_out_percentage

  return kv

def nagios_print(mapped):
  l = ["%s=%s" % (k, mapped[k]) for k in mapped.keys()]
  s = ", ".join(l)

  print 'pepco.py ok|%s' % s
  
def main():
  xml = download()
  mapped = summarize(xml)
  nagios_print(mapped)


if __name__ == '__main__':
  main()
