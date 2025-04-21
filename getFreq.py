import requests
from bs4 import BeautifulSoup
import subprocess
import datetime
import json

# Step 1: 웹 페이지에서 데이터 추출
url = "https://www.short-wave.info/index.php?station=*%27"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', id='output')

# Step 2: 테이블에서 필요한 데이터 추출
data = []
for row in table.find_all('tr')[1:]:  # 첫 번째 행은 헤더이므로 제외
    try:
        cols = row.find_all('td')
        freq = cols[0].text.strip()
        station = cols[1].text.strip()
        language = cols[5].text.strip()
        data.append({'frequency': freq, 'station': station, 'language': language})
        print(f"{freq} {station} {language}")
    except:
        print("Ignore this row")
        pass

# Step 3: JSON 작성 규칙에 따라 데이터 구조화
bookmarks = {}
for i, entry in enumerate(data):
    station_name = entry['station']
    if station_name in bookmarks:
        count = 1
        while f"{station_name}({count})" in bookmarks:
            count += 1
        station_name = f"{station_name}({count})"
    
    bookmarks[station_name] = {
        "bandwidth": 150000.0,
        "frequency": float(entry['frequency']) * 1000,
        "mode": 2
    }

json_data = {
    "bookmarks": bookmarks
}

# Step 4: JSON 파일로 저장
with open('frequency_manager_list.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

print("JSON 파일이 성공적으로 저장되었습니다.")
print("Frequency Manager에서 Import하여 사용하세요.")

# Step 5: GitHub에 파일 커밋
# 커밋 메시지는 [Update] 현재시간 frequency_manager_list.json 형식으로 작성
repo_path="git@github.com:bsy0317/SDRPlusPlus-Frequency-DataBase.git"
commit_msg = f"[Update] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} frequency_manager_list.json"
# 만약 SDRPlusPlus-Frequency-DataBase 폴더가 있다면 삭제
subprocess.run(["rm", "-rf", "SDRPlusPlus-Frequency-DataBase"])
subprocess.run(["git", "clone", repo_path])
subprocess.run(["cp", "frequency_manager_list.json", "SDRPlusPlus-Frequency-DataBase"])
# subprocess.run(["rm", "frequency_manager_list.json"])
subprocess.run(["git", "add", "."], cwd="SDRPlusPlus-Frequency-DataBase")
subprocess.run(["git", "commit", "-m", commit_msg], cwd="SDRPlusPlus-Frequency-DataBase")
subprocess.run(["git", "push"], cwd="SDRPlusPlus-Frequency-DataBase")
print("GitHub에 파일이 성공적으로 업로드되었습니다.")