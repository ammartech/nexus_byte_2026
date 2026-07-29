/* =====================================================
   ResumeFit — Shared Script
   Handles: mobile navigation, before/after comparison
   slider, resume optimizer interaction, and contact
   form validation.
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {
   
   /*  Dark mode Toggle */
   let darkmode = localStorage.getItem('darkmode');
   const themeSwitch = document.getElementById('theme-switch');

   const enableDarkmode = () => {
      document.body.classList.add('darkmode');
      localStorage.setItem('darkmode', 'active');
    }
   const disableDarkmode = () => {
      document.body.classList.remove('darkmode');
      localStorage.setItem('darkmode', null);
    }
   if(darkmode === "active") enableDarkmode();

   themeSwitch.addEventListener("click", () => {
      darkmode = localStorage.getItem('darkmode');
      darkmode !== "active" ? enableDarkmode() : disableDarkmode();
    });
   // Text-to-Speech
const ttsBtn = document.getElementById('tts-btn');

if (ttsBtn && 'speechSynthesis' in window) {

  ttsBtn.addEventListener('click', () => {

    // If already speaking, stop it
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      ttsBtn.textContent = '🔊 Listen';
      ttsBtn.classList.remove('is-speaking');
      return;
    }

    // Grab all readable text on the page
    const content = document.getElementById('main-content');
    const text = content ? content.innerText : document.body.innerText;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1;    // speed: 0.5 to 2
    utterance.pitch = 1;   // tone: 0 to 2

    // Update button when done
    utterance.onend = () => {
      ttsBtn.textContent = '🔊 Listen';
      ttsBtn.classList.remove('is-speaking');
    };

    ttsBtn.textContent = '⏹ Stop';
    ttsBtn.classList.add('is-speaking');
    window.speechSynthesis.speak(utterance);
  });

} else if (ttsBtn) {
  // Hide button if browser doesn't support TTS
  ttsBtn.style.display = 'none';
}

  /* ---------- Mobile Navigation Toggle ---------- */
  var navToggle = document.querySelector(".nav__toggle");
  var navLinks = document.querySelector(".nav__links");

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      var isOpen = navLinks.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    /* Close menu when a link is selected (mobile) */
    navLinks.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.innerWidth <= 640) {
          navLinks.classList.remove("is-open");
          navToggle.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  /* ---------- Before / After Comparison Slider ---------- */
  var compare = document.querySelector(".compare");
  if (compare) {
    var afterPanel = compare.querySelector(".compare__panel--after");
    var handle = compare.querySelector(".compare__handle");
    var rangeInput = compare.querySelector(".compare__slider");

    function setComparePosition(percent) {
      percent = Math.min(100, Math.max(0, percent));
      afterPanel.style.clipPath = "inset(0 0 0 " + percent + "%)";
      handle.style.left = percent + "%";
      if (rangeInput) {
        rangeInput.value = percent;
        rangeInput.setAttribute("aria-valuenow", Math.round(percent));
      }
    }

    /* Keyboard / range input control (accessible alternative to drag) */
    if (rangeInput) {
      rangeInput.addEventListener("input", function () {
        setComparePosition(Number(rangeInput.value));
      });
    }

    /* Drag interaction with mouse */
    var isDragging = false;

    function updateFromClientX(clientX) {
      var rect = compare.getBoundingClientRect();
      var percent = ((clientX - rect.left) / rect.width) * 100;
      setComparePosition(percent);
    }

    handle.addEventListener("mousedown", function () {
      isDragging = true;
    });

    document.addEventListener("mouseup", function () {
      isDragging = false;
    });

    document.addEventListener("mousemove", function (e) {
      if (isDragging) {
        updateFromClientX(e.clientX);
      }
    });

    /* Touch support */
    handle.addEventListener("touchstart", function () {
      isDragging = true;
    }, { passive: true });

    document.addEventListener("touchend", function () {
      isDragging = false;
    });

    document.addEventListener("touchmove", function (e) {
      if (isDragging && e.touches[0]) {
        updateFromClientX(e.touches[0].clientX);
      }
    }, { passive: true });

    /* Initialize at 50% */
    setComparePosition(50);
  }

  /* ---------- Home Page Dropzone Preview (non-functional preview only) ---------- */
  var homeDropzone = document.querySelector(".dropzone[aria-label*='Upload your resume']");
  var homeFileInput = document.querySelector("#resume-file-home");
  var homeFileStatus = document.querySelector("#file-status-home");

  if (homeDropzone && homeFileInput) {
    homeDropzone.addEventListener("click", function () {
      homeFileInput.click();
    });
    homeDropzone.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        homeFileInput.click();
      }
    });
    homeFileInput.addEventListener("change", function () {
      if (homeFileInput.files && homeFileInput.files.length > 0 && homeFileStatus) {
        homeFileStatus.textContent = "Selected file: " + homeFileInput.files[0].name + " — continue to the optimizer to run your check.";
      }
    });
  }

  /* ---------- Resume Optimizer (Upload Page) ---------- */
  var dropzone = document.querySelector("#optimizer-form .dropzone, .dropzone:not([aria-label*='Upload your resume'])");
  var fileInput = document.querySelector("#resume-file");
  var fileStatus = document.querySelector("#file-status");
  var optimizerForm = document.querySelector("#optimizer-form");
  var feedbackPanel = document.querySelector("#feedback");
  var jobDescriptionField = document.querySelector("#job-description");

  if (dropzone && fileInput) {
    /* Click / keyboard activation opens the file picker */
    dropzone.addEventListener("click", function () {
      fileInput.click();
    });

    dropzone.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        fileInput.click();
      }
    });

    fileInput.addEventListener("change", function () {
      if (fileInput.files && fileInput.files.length > 0) {
        fileStatus.textContent = "Selected file: " + fileInput.files[0].name;
      }
    });

    /* Drag and drop visual feedback */
    ["dragenter", "dragover"].forEach(function (eventName) {
      dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        dropzone.classList.add("is-dragover");
      });
    });

    ["dragleave", "drop"].forEach(function (eventName) {
      dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        dropzone.classList.remove("is-dragover");
      });
    });

    dropzone.addEventListener("drop", function (e) {
      var files = e.dataTransfer.files;
      if (files && files.length > 0) {
        fileInput.files = files;
        fileStatus.textContent = "Selected file: " + files[0].name;
      }
    });
  }

  /* Keyword bank used for simple keyword-matching demo */
  var KEYWORD_BANK = [
    "communication", "leadership", "javascript", "html", "css",
    "project management", "teamwork", "problem solving", "python",
    "data analysis", "customer service", "sql", "agile", "research",
    "design", "marketing", "writing", "accessibility", "testing", "git"
  ];

  if (optimizerForm) {
    optimizerForm.addEventListener("submit", function (e) {
      e.preventDefault();

      var hasFile = fileInput && fileInput.files && fileInput.files.length > 0;
      var jobText = jobDescriptionField ? jobDescriptionField.value.trim() : "";

      /* Validate required inputs with clear feedback */
      var jdField = jobDescriptionField.closest(".field");
      if (jobText.length === 0) {
        jdField.classList.add("has-error");
        jobDescriptionField.focus();
        return;
      } else {
        jdField.classList.remove("has-error");
      }

      if (!hasFile) {
        fileStatus.textContent = "Please add your resume file before running the check.";
        fileStatus.style.color = "var(--color-error)";
        return;
      }

      runOptimizerDemo(jobText);
    });
  }

  function runOptimizerDemo(jobText) {
    var lowerJob = jobText.toLowerCase();

    /* Find which bank keywords appear in the pasted job description */
    var relevantKeywords = KEYWORD_BANK.filter(function (word) {
      return lowerJob.indexOf(word) !== -1;
    });

    /* Fallback set so the demo always has content to show */
    if (relevantKeywords.length === 0) {
      relevantKeywords = ["communication", "teamwork", "problem solving", "leadership"];
    }

    /* Simulate a "found in resume" subset for the demo */
    var foundCount = Math.max(1, Math.ceil(relevantKeywords.length / 2));
    var found = relevantKeywords.slice(0, foundCount);
    var missing = relevantKeywords.slice(foundCount);

    var score = Math.round((found.length / relevantKeywords.length) * 100);
    if (score < 35) score = 35 + Math.floor(Math.random() * 10);

    /* Update score display */
    var scoreValue = document.querySelector("#score-value");
    var scoreFill = document.querySelector("#score-fill");
    if (scoreValue) scoreValue.textContent = score + "%";
    if (scoreFill) {
      scoreFill.style.width = "0%";
      requestAnimationFrame(function () {
        scoreFill.style.width = score + "%";
      });
    }

    /* Populate keyword chips */
    var chipWrap = document.querySelector("#keyword-chips");
    if (chipWrap) {
      chipWrap.innerHTML = "";
      found.forEach(function (word) {
        chipWrap.appendChild(createChip(word, true));
      });
      missing.forEach(function (word) {
        chipWrap.appendChild(createChip(word, false));
      });
    }

    /* Populate suggestion list */
    var suggestionsList = document.querySelector("#suggestions-list");
    if (suggestionsList) {
      var suggestions = buildSuggestions(missing, score);
      suggestionsList.innerHTML = "";
      suggestions.forEach(function (item) {
        var li = document.createElement("li");

        var tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = item.tag;

        var text = document.createElement("span");
        text.textContent = item.text;

        li.appendChild(tag);
        li.appendChild(text);
        suggestionsList.appendChild(li);
      });
    }

    /* Reveal the feedback panel and move focus for keyboard/screen-reader users */
    if (feedbackPanel) {
      feedbackPanel.classList.add("is-visible");
      feedbackPanel.setAttribute("tabindex", "-1");
      feedbackPanel.focus();
      feedbackPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }

  function createChip(word, isFound) {
    var chip = document.createElement("span");
    chip.className = "chip " + (isFound ? "chip--found" : "chip--missing");
    chip.textContent = (isFound ? "Found: " : "Missing: ") + word;
    return chip;
  }

  function buildSuggestions(missingKeywords, score) {
    var suggestions = [];

    if (score < 60) {
      suggestions.push({
        tag: "Summary",
        text: "Improve your summary section so it reflects the role's core requirements in the first two lines."
      });
    }

    if (missingKeywords.length > 0) {
      suggestions.push({
        tag: "Keywords",
        text: "Add more technical skills, such as " + missingKeywords.slice(0, 3).join(", ") + ", if they genuinely apply to your experience."
      });
    }

    suggestions.push({
      tag: "Formatting",
      text: "Use consistent date formats and standard section headings so ATS software can read your resume correctly."
    });

    suggestions.push({
      tag: "Achievements",
      text: "Quantify your achievements with numbers, such as percentages, amounts, or time saved, wherever possible."
    });

    if (score >= 60) {
      suggestions.push({
        tag: "Polish",
        text: "Your keyword match is strong. Focus next on trimming unrelated experience to keep the resume concise."
      });
    }

    return suggestions;
  }

  /* ---------- Contact Form Validation ---------- */
  var contactForm = document.querySelector("#contact-form");

  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();

      var name = document.querySelector("#contact-name");
      var email = document.querySelector("#contact-email");
      var message = document.querySelector("#contact-message");
      var status = document.querySelector("#form-status");

      var isValid = true;

      isValid = validateField(name, function (value) {
        return value.trim().length >= 2;
      }, "Enter your full name (at least 2 characters).") && isValid;

      isValid = validateField(email, function (value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
      }, "Enter a valid email address, like name@example.com.") && isValid;

      isValid = validateField(message, function (value) {
        return value.trim().length >= 10;
      }, "Your message should be at least 10 characters long.") && isValid;

      if (!isValid) {
        status.className = "form-status is-error";
        status.textContent = "Please fix the highlighted fields and try again.";
        status.setAttribute("role", "alert");
        return;
      }

      /* Simulate successful submission */
      status.className = "form-status is-success";
      status.textContent = "Thanks, " + name.value.trim().split(" ")[0] + ". Your message has been sent and our team will reply within one business day.";
      status.setAttribute("role", "status");
      contactForm.reset();

      document.querySelectorAll("#contact-form .field").forEach(function (field) {
        field.classList.remove("has-error");
      });
    });
  }

  function validateField(input, testFn, errorMessage) {
    var field = input.closest(".field");
    var errorEl = field.querySelector(".field-error");
    var valid = testFn(input.value);

    if (valid) {
      field.classList.remove("has-error");
    } else {
      field.classList.add("has-error");
      if (errorEl) errorEl.textContent = errorMessage;
    }

    return valid;
  }

});
