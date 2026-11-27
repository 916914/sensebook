// SPDX-License-Identifier: Apache-2.0
import type { MetadataRoute } from "next";
import { nav, site } from "@/content/site";

export default function sitemap(): MetadataRoute.Sitemap {
  return ["/", ...nav.map((n) => n.href)].map((path) => ({ url: new URL(path, site.url).toString() }));
}
