__author__ = 'Joe'
import groceryFileIO

out_dir = "..\\old-recipes\\"
dict = groceryFileIO.read_recipe_file("master_recipe_list.json")

for i in dict:
    file_name=i+".txt"
    out_file=open(out_dir+file_name, "w+")
    out_file.write("##Tags\n")
    for tag in dict[i].tags:
        out_file.write(tag+"\n")
    out_file.write("##Ingredients\n")
    for ingredient in dict[i].ingredients:
        out_file.write(ingredient+"\n")
    out_file.write("##Recipe\n")
