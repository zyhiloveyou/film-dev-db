#!/bin/bash
# 一键：重新构建网站数据 + 同步根目录部署文件（GitHub Pages 从根目录部署）
set -e
cd "$(dirname "$0")"
python3 build_web_data.py
cp web/index.html ./index.html
cp web/data_web.js ./data_web.js
echo "✅ 已构建并同步根目录 index.html / data_web.js"
ls -la index.html data_web.js web/data_web.js | awk '{print $5, $9}'
