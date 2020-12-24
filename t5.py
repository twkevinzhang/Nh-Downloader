import os,time

start=1
end=2161
fragment=250

for i in range(start,end,fragment):
    last=i+fragment
    if i+fragment>end:
        last=end
    if last<end:
        last-=1
    cmd=f"start cmd /c python main.py {i} {last} ^& pause"
    os.system(cmd)
    time.sleep(3)
    print(cmd)
