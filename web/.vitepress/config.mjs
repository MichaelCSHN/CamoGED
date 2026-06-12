export default {
  title: "CamoGED",
  base: "/CamoGED/",
  description: "Camouflage: Generation · Evaluation · Detection",
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Book", link: "https://michaelcshn.github.io/CamoGED/book/" },
      { text: "Demo", link: "/demo" },
      {
        text: "Awesome",
        items: [
          { text: "Overview", link: "/awesome" },
          { text: "Papers", link: "/papers" },
          { text: "Code", link: "/models" },
          { text: "Leaderboard", link: "/leaderboard" },
          { text: "Datasets", link: "/datasets" }
        ]
      }
    ],
    socialLinks: [
      { icon: "github", link: "https://github.com/MichaelCSHN/CamoGED" }
    ],
    search: { provider: "local" }
  }
}
