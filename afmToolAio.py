import sys

assert len(sys.argv) > 1
print(f"arg passed in are")
for arg in sys.argv[1:]:
    print(arg)
print("1: to calculate map info")
print("2: to cut map")
work = input()
if work == "1":
    import afm.autofreshmap_calcmapinfo

    afm.autofreshmap_calcmapinfo.main()
elif work == "2":
    import afm.autofreshmap_cutmap

    afm.autofreshmap_cutmap.main()
