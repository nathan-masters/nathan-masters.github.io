---
layout: post
title:  "Interactive Bokeh: UK/Swiss Covid Comparisons"
date:   2020-05-11 19:44:27 +0200
author: Nathan
---

# Confinement is in progress... and so is this website.

An update from my previous post. My previous post presented some data compiled in Python
and using matplotlib to output a static post.

Since then, I've tried to see if I can present this data in a slightly more interactive way.
Along comes "Bokeh" to save the day - or at least help a little. A little fiddly to work out,
but not too tricky, it presents nice enough plots, which didn't require too much new learning.
All the compilation into html is performed for you, and simple inclusion into R markdown script
means you can all see it.

Currently residing in Switzerland, and originally from the UK, it's a little worrying to see
how the two countries outcomes are so different...

These graphs use the easily available data from the [European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide){:target="_blank"}.


A little difficulty I had in particular with Bokeh, was scaling the legend responsively with 
page width. So sorry if you're looking at this on a small screen :(

<iframe src="/assets/img/Bokeh/UK-CH_corona.html"
    sandbox="allow-same-origin allow-scripts"
    width="100%"
    height="650"
    scrolling="no"
    float="centre"
    seamless="seamless"
    frameborder="0">
</iframe>
