// Resource navigation intentionally separates the curated Awesome view from the full Catalog.
export default {
  title: "CamoGED",
  base: "/CamoGED/",
  description: "CamoGED research preview: monograph, curated resources, verified metadata, and evaluation tools.",
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Book", link: "/book/" },
      {
        text: "Resources",
        items: [
          { text: "Awesome Camouflage", link: "/awesome" },
          { text: "Research Catalog", link: "/catalog" },
          { text: "Update status", link: "/updates" },
          { text: "Datasets", link: "/datasets" },
          { text: "Code & Resources", link: "/models" },
          { text: "Verified results", link: "/leaderboard" }
        ]
      },
      { text: "Synthetic demo", link: "/demo" }
    ],
    sidebar: {
      "/": [
        {
          text: "CamoGED",
          items: [
            { text: "Home", link: "/" },
            { text: "Awesome Camouflage", link: "/awesome" },
            { text: "Research Catalog", link: "/catalog" },
            { text: "Update status", link: "/updates" },
            { text: "Datasets", link: "/datasets" },
            { text: "Code & Resources", link: "/models" },
            { text: "Verified results", link: "/leaderboard" },
            { text: "Synthetic demo", link: "/demo" }
          ]
        }
      ]
    },
    socialLinks: [{ icon: "github", link: "https://github.com/MichaelCSHN/CamoGED" }],
    search: { provider: "local" }
  }
};
