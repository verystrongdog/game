#!/bin/bash
# grilling #87 — 一手叙事文献批量下载
# 来源: .scratch/grilling-87-npc-material/ref/精神病人住院传记-检索记录.md §二
set -u
OUT=".scratch/grilling-87-npc-material/ref/一手叙事"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
LOG="$OUT/下载日志.txt"
: > "$LOG"

dl() { # $1=url  $2=文件名slug  $3=来源标签
  local url="$1" slug="$2" tag="$3"
  local f="$OUT/$slug.html"
  local code
  code=$(curl -sL -A "$UA" --max-time 30 -o "$f" -w "%{http_code}" "$url" 2>/dev/null)
  local size=0
  [ -f "$f" ] && size=$(stat -c%s "$f" 2>/dev/null || echo 0)
  if [ "$code" = "200" ] && [ "$size" -gt 500 ]; then
    echo "OK   [$code ${size}B] $slug  ($tag)" | tee -a "$LOG"
  else
    echo "FAIL [$code ${size}B] $slug  ($tag) $url" | tee -a "$LOG"
    rm -f "$f"
  fi
}

dl "https://m.jfdaily.com/wx/detail.do?id=405024" "01-李兰妮-解放日报-住进精神病院的深圳作协主席" "李兰妮/旷野无人"
dl "https://www.163.com/dy/article/GJQKO3S6055040N3.html" "02-李兰妮-网易-住进精神病院的作协主席" "李兰妮/旷野无人"
dl "https://book.douban.com/subject/3123690/" "03-旷野无人-豆瓣条目" "李兰妮/旷野无人"
dl "https://news.ycwb.com/2021-08/19/content_40214352.htm" "04-李兰妮-羊城晚报-他们只是病了不是变态" "李兰妮/野地灵光"
dl "http://www.chinawriter.com.cn/n1/2021/0729/c405086-32174379.html" "05-野地灵光-中国作家网书汇" "李兰妮/野地灵光"
dl "https://www.thecover.cn/news/8083108" "06-李兰妮-封面新闻-当一位作家住进精神病医院" "李兰妮/野地灵光"
dl "https://www.163.com/dy/article/EGEHAA3A05148GQ0.html" "07-左灯-网易-要好好活着啊老铁38天" "左灯/我在精神病院抗抑郁"
dl "https://read.douban.com/ebook/109202659/" "08-我在精神病院抗抑郁-豆瓣阅读条目" "左灯/我在精神病院抗抑郁"
dl "https://www.sohu.com/a/322832040_206391" "09-左灯-搜狐-38天" "左灯/我在精神病院抗抑郁"
dl "https://www.thepaper.cn/newsDetail_forward_1379854" "10-张进-澎湃-媒体人的受难记" "张进/渡过"
dl "https://zhangjin.blog.caixin.com/archives/140055" "11-张进-财新博客-央视面对面文字版" "张进/渡过"
dl "http://www.sunofus.org/bbs/thread-2135583-6-7.html" "12-阳光工程-每天都在医院已经2年了" "网络自述/论坛"
dl "https://www.douban.com/group/topic/253914614/" "13-豆瓣-我做过MECT治疗" "网络自述/MECT"
dl "https://wsa.jianshu.io/p/26687f184e09" "14-简书-医院内精神病患者日常故事" "网络自述/简书"

echo "=== 完成 ===" >> "$LOG"
