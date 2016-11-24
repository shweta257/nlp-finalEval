# import xml.dom.minidom

import xml.dom.minidom as d

# dom = d.parse("temp.xml")
#
# for node in dom.getElementsByTagName('text'):  # visit every node <bar />
#     node.setAttribute('id',1)
#
# print dom.toprettyxml()

xmlData = d.parse("temp.xml")

# itmNode = xmlData.getElementsByTagName("item")
# for n in itmNode:
#     # n.childNodes[1] = n.childNodes[3]
#     # n.childNodes[1].tagName = "link"
#     print type(n)
#     print n.childNodes[1]

collection = xmlData.documentElement

for data in collection.childNodes:
    print data.nodeName
    if data.nodeName == "COREF":
        # print data.getAttribute("ID")
        # data.setAttribute("IDD", "4")
        attr = xmlData.createAttribute("IDD")
        attr.value = "5"
        data.setAttributeNode(attr)

for data in collection.childNodes:
    print data.nodeName
    if data.nodeName == "COREF":
        print data.getAttribute("IDD")
        print data.getAttribute("ID")
        # data.setAttribute("REF", 4)
    # print data.getAttribute("ID")

print xmlData.toxml()