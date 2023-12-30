const BuiltWith = require("builtwith-api");
const fs = require("fs");
const path = require("path");

require("dotenv").config();

const builtwith = BuiltWith(process.env.BUILTWITH_API_KEY, {
  responseFormat: "json",
});

const technologies = ["Salesforce"];

async function fetchBuiltWithLists() {
  const bw = await builtwith.lists(technologies, {
    includeMetaData: true,
    offset: "oQEwEnH2FJuIzeXOEk2T",
    since: "2022-01-01",
  });

  if (!bw.results || bw.results.length === 0) {
    console.error("No results found.");
    return;
  }

  const domains = bw.results.map((result) => result.domain).join("\n");

  const dir = "./initial_bw/";
  const fileName = `domains_${new Date().getTime()}.txt`;

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(path.join(dir, fileName), domains);

  return fileName;
}

fetchBuiltWithLists()
  .then((fileName) => {
    console.log(`Domains saved to ${fileName} in initial_bw/ directory...`);
  })
  .catch((error) => {
    console.error("Error fetching data:", error);
  });
// oQEwEnH2FJuIzeXOEk2T
