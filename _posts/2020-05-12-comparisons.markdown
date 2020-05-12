---
layout: post
title:  "Interactive Bokeh: Direct Comparisons"
date:   2020-05-12 13:24:27 +0200
author: Nathan
---

# Confinement is in progress... and so is this website.

Just a quick post to present the direct comparison of cumulative deaths for a number of
countries. This data is accurate as of the 12th May.

It turns out Bokeh's use of a dedicated Source Data Structure makes quick changes a little
difficult. Another thing I haven't quite worked out is the scale of the x-axis...

These graphs use the easily available data from the [European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide){:target="_blank"}.

<iframe src="/assets/img/Bokeh/corona-comparisons.html"
    sandbox="allow-same-origin allow-scripts"
    width="100%"
    height="800"
    scrolling="no"
    float="centre"
    seamless="seamless"
    frameborder="0">
</iframe>
