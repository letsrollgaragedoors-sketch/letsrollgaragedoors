# blog.html — 4 Targeted Fixes

Apply these changes directly in your GitHub repo editor or via GitHub Desktop.
Each section shows the exact OLD text to find and the NEW text to replace it with.

---

## FIX 1 — Dead link: insulated-garage-doors-austin.html (in art8)

### FIND (exact):
```
<a href="insulated-garage-doors-austin.html">guide to insulated garage doors</a>
```

### REPLACE WITH:
```
<a href="garage-door-installation-austin.html">guide to garage door installation and insulation options</a>
```

---

## FIX 2 — Dead link: same-day-garage-door-service-austin.html (in art8)

### FIND (exact):
```
<a href="same-day-garage-door-service-austin.html">same-day garage door service</a>
```

### REPLACE WITH:
```
<a href="garage-door-repair-austin.html">same-day garage door service</a>
```

---

## FIX 3 — AggregateRating reviewCount (in the JSON-LD <script> block near top of blog.html)

UPDATE THIS when you know your real Google + Yelp review total.
The current value "5" only counts the 5 inline testimonials, not your actual review count.

### FIND (exact):
```
"aggregateRating": {
"@type": "AggregateRating",
"ratingValue": "5.0",
"reviewCount": "5",
"bestRating": "5"
},
```

### REPLACE WITH (example — use YOUR real review count):
```
"aggregateRating": {
"@type": "AggregateRating",
"ratingValue": "4.9",
"reviewCount": "45",
"bestRating": "5",
"worstRating": "1"
},
```

NOTE: Use your real Google review count + Yelp review count combined, or just Google if that's your primary.
Check your Google Business Profile for the current number before updating.

---

## FIX 4 — Add BlogPosting schema for all 5 articles

Find the CLOSING </script> tag of the existing JSON-LD block (near line 170 in blog.html).
It will look like this in context:

### FIND (exact — the closing of the existing schema block):
```
]
}
</script>
```
(This is the closing of the @graph array inside the first <script type="application/ld+json"> block)

### REPLACE WITH:
```
]
}
</script>

<!-- BlogPosting schema — one block per article for AI/search citation -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://www.letsrollgaragedoors.com/blog.html#art1",
  "headline": "7 Warning Signs Your Garage Door Spring Is About to Break",
  "description": "A broken torsion spring is one of the most dangerous garage door failures. Learn the 7 warning signs Austin homeowners should watch for before a spring fails completely.",
  "datePublished": "2026-06-02",
  "dateModified": "2026-06-02",
  "author": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "url": "https://www.letsrollgaragedoors.com/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.letsrollgaragedoors.com/logo.png"
    }
  },
  "image": "https://www.letsrollgaragedoors.com/images/img-a1337081c6a5.webp",
  "url": "https://www.letsrollgaragedoors.com/blog.html#art1",
  "keywords": "garage door spring warning signs, broken torsion spring Austin, garage door spring replacement Austin TX",
  "articleSection": "Safety",
  "about": {
    "@type": "Service",
    "name": "Garage Door Spring Replacement",
    "provider": {
      "@type": "LocalBusiness",
      "name": "Let's Roll Garage Doors",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Austin",
        "addressRegion": "TX"
      }
    }
  },
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Can I replace a garage door spring myself?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "No. Torsion springs are under extreme tension and can cause severe injury or death if handled without the right tools and training. This is one repair that should always be left to a certified technician."
        }
      },
      {
        "@type": "Question",
        "name": "How much does it cost to replace a broken garage door spring in Austin?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "In Austin, single torsion spring replacement typically runs $150–$250, while a two-spring system is usually $200–$350. We always recommend replacing both springs together since they wear at a similar rate."
        }
      },
      {
        "@type": "Question",
        "name": "How long do garage door springs typically last?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Standard torsion springs are rated for about 10,000 cycles, roughly 7 years for an average household. High-cycle springs rated for 25,000–50,000 cycles are available and last considerably longer."
        }
      },
      {
        "@type": "Question",
        "name": "Is it safe to use my garage door if a spring is broken?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "No. A broken spring means the door has lost its counterbalance, putting excess strain on the opener and cables and creating a real risk of the door falling. Avoid using the door and call for emergency service."
        }
      }
    ]
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://www.letsrollgaragedoors.com/blog.html#art2",
  "headline": "How Much Does Garage Door Repair Cost in Austin, TX? (2026 Guide)",
  "description": "Honest, up-to-date breakdown of garage door repair costs in Austin for 2026. Spring replacement, opener repair, cable repair, new door installation pricing with no hidden fees.",
  "datePublished": "2026-05-28",
  "dateModified": "2026-05-28",
  "author": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "url": "https://www.letsrollgaragedoors.com/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.letsrollgaragedoors.com/logo.png"
    }
  },
  "image": "https://www.letsrollgaragedoors.com/images/img-d8d103469b7c.webp",
  "url": "https://www.letsrollgaragedoors.com/blog.html#art2",
  "keywords": "garage door repair cost Austin TX, how much does garage door repair cost Austin, garage door spring replacement cost Austin 2026",
  "articleSection": "Pricing",
  "about": {
    "@type": "Service",
    "name": "Garage Door Repair",
    "provider": {
      "@type": "LocalBusiness",
      "name": "Let's Roll Garage Doors",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Austin",
        "addressRegion": "TX"
      }
    }
  },
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "How much does garage door spring replacement cost in Austin?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Torsion spring replacement in Austin typically runs $150–$250 for a single spring and $200–$350 for a two-spring system. Always replace both springs at the same time."
        }
      },
      {
        "@type": "Question",
        "name": "How much does emergency garage door repair cost after hours in Austin?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Most companies, including Let's Roll Garage Doors, add a $50–$100 after-hours or weekend service fee on top of the repair cost. This fee is disclosed upfront before any work begins."
        }
      },
      {
        "@type": "Question",
        "name": "Is it cheaper to repair or replace an old garage door?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "If your door is over 15–20 years old and the repair would cost more than half of a new door's value, replacement is usually the smarter long-term investment."
        }
      },
      {
        "@type": "Question",
        "name": "How much does a new garage door installation cost in Austin?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "A basic single-car steel door installed runs $800–$1,200. Premium materials and double-car widths push costs to $1,500–$2,500 or more."
        }
      }
    ]
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://www.letsrollgaragedoors.com/blog.html#art3",
  "headline": "5 Easy Garage Door Maintenance Tips That Add Years to Its Life",
  "description": "Five garage door maintenance tasks Austin homeowners can do in under 30 minutes to extend door life and prevent costly repairs. Lubrication, balance tests, weather stripping, and more.",
  "datePublished": "2026-05-15",
  "dateModified": "2026-05-15",
  "author": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "url": "https://www.letsrollgaragedoors.com/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.letsrollgaragedoors.com/logo.png"
    }
  },
  "image": "https://www.letsrollgaragedoors.com/images/img-1c0276e8eab4.webp",
  "url": "https://www.letsrollgaragedoors.com/blog.html#art3",
  "keywords": "garage door maintenance Austin TX, how to maintain garage door, garage door tune up tips Austin",
  "articleSection": "Maintenance",
  "about": {
    "@type": "Service",
    "name": "Garage Door Tune-Up & Maintenance",
    "provider": {
      "@type": "LocalBusiness",
      "name": "Let's Roll Garage Doors",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Austin",
        "addressRegion": "TX"
      }
    }
  },
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "How often should I lubricate my garage door?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Every 6 months is a good baseline. Use a white lithium grease or silicone-based lubricant on springs, hinges, rollers, and the opener chain or screw. Never use WD-40 and never lubricate the tracks."
        }
      },
      {
        "@type": "Question",
        "name": "How do I know if my garage door is unbalanced?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Disconnect the opener and manually lift the door about halfway. A balanced door will stay in place. If it falls or shoots upward, the springs need professional adjustment."
        }
      },
      {
        "@type": "Question",
        "name": "How often should I schedule a professional garage door tune-up?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Once a year is the standard recommendation for Austin homeowners. A professional catches wear and hardware issues that are easy to miss during a DIY check."
        }
      }
    ]
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://www.letsrollgaragedoors.com/blog.html#art4",
  "headline": "Smart Garage Door Openers: Is It Worth the Upgrade in 2026?",
  "description": "Are smart garage door openers worth it for Austin homeowners in 2026? We compare the top models — LiftMaster 84505R, Chamberlain B4643T, and Genie ChainMax — with installed pricing.",
  "datePublished": "2026-05-05",
  "dateModified": "2026-05-05",
  "author": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "url": "https://www.letsrollgaragedoors.com/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.letsrollgaragedoors.com/logo.png"
    }
  },
  "image": "https://www.letsrollgaragedoors.com/images/img-17af44cc041a.webp",
  "url": "https://www.letsrollgaragedoors.com/blog.html#art4",
  "keywords": "smart garage door opener Austin TX, LiftMaster myQ Austin, best garage door opener 2026, smart opener installation Austin",
  "articleSection": "Smart Home",
  "about": {
    "@type": "Service",
    "name": "Garage Door Opener Repair & Installation",
    "provider": {
      "@type": "LocalBusiness",
      "name": "Let's Roll Garage Doors",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Austin",
        "addressRegion": "TX"
      }
    }
  },
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the best smart garage door opener in 2026?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "The LiftMaster 84505R is the industry standard best overall — built-in camera, automatic closing timer, myQ app compatibility, roughly $650–$750 installed. For best value, the Chamberlain B4643T offers belt-drive quiet operation and battery backup for $450–$550 installed."
        }
      },
      {
        "@type": "Question",
        "name": "How much does a smart garage door opener cost installed in Austin?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Smart opener installation in Austin ranges from $380–$750 depending on model. Budget chain-drive smart openers start around $380–$450 installed; premium belt-drive models with cameras run $650–$750 installed."
        }
      },
      {
        "@type": "Question",
        "name": "Can a smart garage door opener work with any garage door?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Most smart openers are compatible with standard residential garage doors. Our technicians check compatibility during the estimate and will flag any issues before installation begins."
        }
      }
    ]
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://www.letsrollgaragedoors.com/blog.html#art8",
  "headline": "When Should You Replace Your Garage Door? 10 Signs It's Time for a New Garage Door in Austin, TX",
  "description": "10 signs Austin homeowners should replace their garage door rather than repair it. Covers age, damage, insulation, frequency of repairs, safety, and repair vs. replace cost comparison.",
  "datePublished": "2026-08-12",
  "dateModified": "2026-08-22",
  "author": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "url": "https://www.letsrollgaragedoors.com/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Let's Roll Garage Doors",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.letsrollgaragedoors.com/logo.png"
    }
  },
  "image": "https://www.letsrollgaragedoors.com/images/garage-door-rotting-damaged-austin.jpg",
  "url": "https://www.letsrollgaragedoors.com/blog.html#art8",
  "keywords": "when to replace garage door Austin TX, garage door replacement Austin, repair or replace garage door Austin, new garage door cost Austin",
  "articleSection": "Replacement",
  "about": {
    "@type": "Service",
    "name": "New Garage Door Installation",
    "provider": {
      "@type": "LocalBusiness",
      "name": "Let's Roll Garage Doors",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Austin",
        "addressRegion": "TX"
      }
    }
  },
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Should I repair or replace my garage door in Austin?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Repair makes sense when the door is relatively new, structurally sound, and only one component has failed. Replacement makes more sense when the door is 15–20+ years old, multiple components are failing, it needs frequent repairs, or repair costs exceed 50% of a new door's value."
        }
      },
      {
        "@type": "Question",
        "name": "How long does a garage door last in Texas?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "A typical residential garage door lasts approximately 15–30 years depending on material, maintenance, and climate. Austin's heat, UV exposure, and humidity can accelerate wear on seals, springs, and wooden panels compared to milder climates."
        }
      },
      {
        "@type": "Question",
        "name": "Are insulated garage doors worth it in Austin?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes, for most Austin homeowners with attached garages. Insulated steel doors with polyurethane foam cores reduce heat transfer significantly, which matters when summer temperatures exceed 100°F. They also reduce noise and often qualify for energy efficiency incentives."
        }
      },
      {
        "@type": "Question",
        "name": "How much does garage door replacement cost in Austin?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Cost depends on door size, material, insulation level, and design. A basic single-car steel door replacement starts around $800–$1,200 installed. Premium insulated, carriage-house, or custom designs for double-car garages can run $1,500–$2,500 or more."
        }
      }
    ]
  }
}
</script>
```

---

## SUMMARY OF ALL CHANGES

| Fix | File | What changed |
|-----|------|-------------|
| Dead link 1 | blog.html art8 | `insulated-garage-doors-austin.html` → `garage-door-installation-austin.html` |
| Dead link 2 | blog.html art8 | `same-day-garage-door-service-austin.html` → `garage-door-repair-austin.html` |
| AggregateRating | blog.html schema | Update reviewCount from "5" to your real review count |
| BlogPosting schema | blog.html | Add 5 × BlogPosting+FAQPage blocks after closing </script> of existing schema |

---

## SEPARATE FILE TO DEPLOY

Replace sitemap.xml in your repo with the new sitemap.xml file provided.
Changes: removed 4 phantom URLs that had no corresponding HTML files.
Removed: when-to-replace-garage-door-austin.html, garage-door-spring-warning-signs-austin.html,
garage-door-maintenance-tips-austin.html, smart-garage-door-openers-austin.html
Added: warranty-terms.html (real page, was missing from sitemap)

---

## INDEX.HTML SIZE INVESTIGATION (cannot auto-fix — requires manual inspection)

Your index.html is 3.56 MB. This is ~28x the normal size for a static HTML page.
The most likely cause: base64-encoded images still embedded directly in the HTML or CSS.

HOW TO CHECK:
1. Open index.html in your code editor
2. Search for: `data:image/` — every hit is an inline base64 image
3. Each one should be replaced with an external <img src="images/filename.webp"> reference
   (you already did this work for some images, but at least one large one remains embedded)

You should also check for any large inline <style> blocks that embed base64 font data.
Search for: `data:font/` or `data:application/font`

Once you find the offending data URIs, extract each to /images/ as a .webp file
and reference them externally. The target size for index.html is under 200KB.
