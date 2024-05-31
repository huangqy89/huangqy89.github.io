---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

Education
======
* Postdoc in Computer Science and Engineering, HKUST, 2019
* Ph.D. in Computer Science and Engineering, HKUST, 2018
* B.S. in Computer Science and Engineering, Shanghai Jiao Tong University, 2013

Work experience
======
* December 2022: Associate professor
  * Sun Yat-sen University

* November 2019: A research track faculty
  * Southern University of Science and Technology

* September 2018: Postdoctoral researcher
  * Hong Kong University of Science and Technology

Publications
======
  <ul>{% for post in site.publications reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
  
Talks
======
  <ul>{% for post in site.talks reversed %}
    {% include archive-single-talk-cv.html  %}
  {% endfor %}</ul>
  
Teaching
======
  <ul>{% for post in site.teaching reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
