import DefaultTheme from "vitepress/theme";
import CamoDemo from "./components/CamoDemo.vue";
import "./custom.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("CamoDemo", CamoDemo);
  }
};
