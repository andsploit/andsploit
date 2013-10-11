
def clean(reflector):
    """
    Remove APK and DEX files cached by andsploit.
    """

    context = reflector.resolve('com.mwr.dz.Agent').getContext()
    cache_directory = context.getCacheDir().listFiles()
    
    i = 0
    for f in cache_directory:
        if f.toString().endswith((".apk", ".dex")):
            f.delete()
            
            i += 1
    
    return i
    
