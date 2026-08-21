#!/bin/bash
# 一键打包 APK（在 film-dev-db-beta/apk/ 目录运行）
# 前置：web/ 目录的 index.html + data_web.js 已是最新（改数据后先跑 python3 build_web_data.py）
set -e
cd "$(dirname "$0")"
export JAVA_HOME="$HOME/devtools/jdk21/Contents/Home"
export ANDROID_HOME="$HOME/devtools/android-sdk"
export ANDROID_SDK_ROOT="$HOME/devtools/android-sdk"

echo "== 同步网站文件到 www/ =="
cp ../web/index.html www/
cp ../web/data_web.js www/

echo "== cap sync =="
npx cap sync android

echo "== Gradle 构建（签名 release）=="
cd android && ./gradlew assembleRelease --no-daemon

cd ..
cp android/app/build/outputs/apk/release/app-release.apk "黑白胶片显影时间库-beta.apk"
echo ""
echo "✅ APK 生成：$(pwd)/黑白胶片显影时间库-beta.apk"
ls -la "黑白胶片显影时间库-beta.apk"
