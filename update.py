import lir,os

#remove old stuff
lir.FileSystem.delete("~/.lir/bin")
lir.FileSystem.delete("~/.lir/signals")
lir.FileSystem.delete("~/.lir/actions")
lir.FileSystem.delete("~/.lir/services")
lir.FileSystem.delete("~/.lir/stt")
lir.FileSystem.delete("~/.lir/tts")
lir.FileSystem.delete("~/.lir/plugins")

for d in ["plugins","tts","stt","actions","services","bin"]:
    lir.FileSystem.create_directory("~/.lir/"+d)

dev_plugins = os.listdir("dev_plugins")
for plugin in dev_plugins:
    print(plugin)
    if os.path.isdir("dev_plugins/" + plugin):
        lir.PluginManager.installFolder("dev_plugins/" + plugin)
