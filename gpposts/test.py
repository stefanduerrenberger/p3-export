#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy

text = '&lt;/p&gt;&lt;div class="events-box middle-box left"&gt;&lt;div class="frame"&gt;&lt;a class="open-img EnlargeImage" href="/switzerland/Global/switzerland/axpo-umfrage.png" title=""&gt;            &lt;img id="ctl00_cphContentArea_epiEntryContent_ctl00_ctl02_Image1" class="Thumbnail" src="/switzerland/ReSizes/Medium/Global/switzerland/axpo-umfrage.png" alt="" style="border-width:0px;"&gt;            &lt;span class="btn-open"&gt;Zoom&lt;/span&gt;        &lt;/a&gt;    &lt;/div&gt;    &lt;div class="events-content no-title"&gt;        &lt;span class="date"&gt;&lt;/span&gt;        &lt;strong&gt;&lt;/strong&gt;        &lt;p&gt;            Klares Ja zum Atomausstieg – selbst in Umfrage der Beznau-Betreiberin Axpo (Quelle: «Energiedialog» Axpo, November 2016)        &lt;/p&gt;    &lt;/div&gt;'

remove = '&lt;span class="btn-open"&gt;Zoom&lt;/span&gt;'

text = text.replace(remove, '')

print text


