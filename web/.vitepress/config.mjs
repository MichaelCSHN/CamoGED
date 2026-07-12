export default {
  title: "CamoGED",
  base: "/CamoGED/",
  description: "CamoGED research preview: monograph, verified metadata, and evaluation tools.",
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Book", link: "/book/" },
      { text: "Synthetic demo", link: "/demo" },
      { text: "Papers", link: "/papers" },
      { text: "Datasets", link: "/datasets" },
      { text: "Code & Resources", link: "/models" },
      { text: "Verified results", link: "/leaderboard" }
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/MichaelCSHN/CamoGED" }],
    search: { provider: "local" }
  }
};
