import DefaultTheme from "vitepress/theme";
import AwesomeScanStatus from "./components/AwesomeScanStatus.vue";
import CamoDemo from "./components/CamoDemo.vue";
import CatalogExplorer from "./components/CatalogExplorer.vue";
import "./custom.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("AwesomeScanStatus", AwesomeScanStatus);
    app.component("CamoDemo", CamoDemo);
    app.component("CatalogExplorer", CatalogExplorer);
  }
};
