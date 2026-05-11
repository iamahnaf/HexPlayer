#link ="https://youtube.com/shorts/2N5nTq5GZus?si=PeHisk1Dx7ZDQPmu"
#listofwords= link.split('/')
#domain = listofwords[2].split(".")
#print(domain[1])


from urllib.parse import urlparse

link = "https://facebook.com/share/r/1DZEwUkuPx/"

domain = urlparse(link).netloc

platform = domain.replace("www.", "").split(".")[0]

print(platform)