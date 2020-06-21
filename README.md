# 사지방에서 miniconda 설치하기

* tmp 디렉토리에는 50GB가 할당되어 있으므로 /tmp에 minidonda 다운로드 받기
* 설치: bash 파일명
* yes and yes
* 터미널 재시작
* python extension
* git checkout --track origin/heroku

* pip 미러 변경(사지방에서)
mkdir ~/.pip
cat <<EOF > ~/.pip/pip.conf
 [global]
 index-url = http://mirror.kakao.com/pypi/simple
 trusted-host=mirror.kakao.com
EOF

* pip install -r requirements.txt






* You can view the finished app on [Heroku](https://flying-dog.herokuapp.com/).
* Take a moment to read my [Medium post about deploying Dash apps](https://medium.com/@austinlasseter/how-to-deploy-a-simple-plotly-dash-app-to-heroku-622a2216eb73).
* I also have a gallery of simple Dash apps for learning [here](https://github.com/austinlasseter/plotly_dash_tutorial/blob/master/06%20Heroku%20examples/list%20of%20resources.md).
* If you'd like to learn even more about Plotly Dash, check out my [tutorial repo](https://github.com/austinlasseter/plotly_dash_tutorial) on github!.
* If you'd like to tinker with the colors of your app, try using HEX codes from [HTML Color Codes](https://htmlcolorcodes.com/).
* The `assets` folder contains a file called `favicon.ico` -- you can find and download customized favicons [here](https://www.favicon.cc/). Just replace the current favicon with a new one.
* Plotly Dash apps can only be viewed in a modern browser (like Chrome or Mozilla). They won't render in antediluvian browsers such as Microsoft.
