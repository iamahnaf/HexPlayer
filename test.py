link ="https://www.youtube.com/watch?v=K_-oWRYBkmE"
listofwords= link.split('/')
domain = listofwords[2].split(".")
print(domain[1])