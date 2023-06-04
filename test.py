time = ''

if time and (int(time[:2]) >= 24 or int(time[3:]) >= 60):
    print(11)
