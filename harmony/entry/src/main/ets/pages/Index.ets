import { webview } from '@kit.ArkWeb';
import { BusinessError } from '@kit.BasicServicesKit';

/**
 * 黑白胶片显影时间库
 * Web 组件加载本地打包的站点（rawfile 下的 index.html + data_web.js），完全离线可用。
 */
@Entry
@Component
struct Index {
  controller: webview.WebviewController = new webview.WebviewController();

  build() {
    Column() {
      Web({ src: $rawfile('index.html'), controller: this.controller })
        .javaScriptAccess(true)      // 允许 JS
        .domStorageAccess(true)      // 允许 localStorage（收藏/暗房偏好）
        .fileAccess(true)            // 允许访问 rawfile 资源
        .onlineImageAccess(true)
        .onControllerAttached(() => {
          // 让 Web 页面使用系统暗色模式时自动切换
        })
        .onErrorReceive((event: WebResourceError) => {
          console.error('FilmDev load error: ' + JSON.stringify(event.error));
        })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#121418')
  }
}
