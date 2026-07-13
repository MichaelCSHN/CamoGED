import DefaultTheme from "vitepress/theme";
import CamoDemo from "./components/CamoDemo.vue";
import CatalogExplorer from "./components/CatalogExplorer.vue";
import ScanStatus from "./components/ScanStatus.vue";
import "./custom.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("CamoDemo", CamoDemo);
    app.component("CatalogExplorer", CatalogExplorer);
    app.component("ScanStatus", ScanStatus);
  }
};
