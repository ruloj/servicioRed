nombres = [
    '1 = STRING: "Physical memory"\t\t',
    '3 = STRING: "Virtual memory"\t\t',
    '6 = STRING: "Memory buffers"\t\t',
    '7 = STRING: "Cached memory"\t\t',
    '8 = STRING: "Shared memory"\t\t',
    '10 = STRING: "Swap space"\t\t',
    '35 = STRING: "/run"\t\t\t',
    '36 = STRING: "/"\t\t\t',
    '38 = STRING: "/dev/shm"\t\t\t',
    '39 = STRING: "/run/lock"\t\t',
    '40 = STRING: "/sys/fs/cgroup"\t\t',
    '79 = STRING: "/boot/efi"\t\t',
    '80 = STRING: "/run/user/1000"\t\t',
    '83 = STRING: "/run/snapd/ns"\t\t',
]

total = [
    3943824,
    2025468,
    595108,
    77976,
    1918356,
    50637,
    10125888,
    253183,
    1280,
    253183,
    130812,
    50636,
    50637,
]

used =[
    1912484,
    3004860,
    14756,
    562580,
    111180,
    1092376,
    386,
    3488833,
    9440,
    1,
    0,
    1,
    21,
    386,
]

units = [
    1024,
    1024,
    1024,
    1024,
    1024,
    1024,
    4096,
    4096,
    4096,
    4096,
    4096,
    4096,
    4096,
    4096,
]

for i in range(len(total)):
    mult = total[i] * units[i]
    res = "{:.2f}".format(mult * 1e-9)
    print(nombres[i] + ' - ' + res, end='\t - \t')
    mult = used[i] * units[i]
    res = "{:.2f}".format(mult * 1e-9)
    print(res)

    # res = total[i] * 4.096e-6
    # print(nombres[i],end=' - ')
    # print(res, end='\t - \t')
    # res = used[i] * 4.096e-6
    # print(res)
    #snmpwalk -v2c -c comunidadRulo localhost 1.3.6.1.2.1.25.2.3.1.6
