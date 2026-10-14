/*
 * prepza embed, v1: a candidate's interview inside your own site.
 *
 *   <div id="interview"></div>
 *   <script src="https://prepza.ai/embed/v1.js"></script>
 *   <script>
 *     Prepza.embed({
 *       element: "#interview",
 *       // The invite_url your server got from POST /v1/interviews/{id}/candidates.
 *       url: "https://prepza.ai/invite/3fTq9xLk2VbN7wZr8YcP1mHd5sJ4gAe6uQo0RiKtEy",
 *       onFinish: ({ candidateId }) => {},
 *     })
 *   </script>
 *
 * Only a candidate invited with sign_in false, and only on your company's verified website
 * domain (and its subdomains): anywhere else the frame stays empty.
 */
;(function () {
  "use strict"

  var ORIGIN = new URL(document.currentScript.src).origin
  var SOURCE = "prepza"
  var MIN_HEIGHT = 640

  function embed(options) {
    var element =
      typeof options.element === "string"
        ? document.querySelector(options.element)
        : options.element

    if (!element) {
      throw new Error("Prepza.embed: no element " + options.element)
    }

    var token = new URL(options.url).pathname.split("/").filter(Boolean).pop()
    var frame = document.createElement("iframe")
    frame.src =
      ORIGIN +
      "/embedded/" +
      encodeURIComponent(token) +
      "?origin=" +
      encodeURIComponent(window.location.origin)
    frame.title = options.title || "Interview"
    frame.style.cssText =
      "display:block;width:100%;border:0;height:" + MIN_HEIGHT + "px"

    function listen(event) {
      var data = event.data || {}

      if (
        event.origin !== ORIGIN ||
        event.source !== frame.contentWindow ||
        data.source !== SOURCE
      ) {
        return
      }

      if (data.type === "resize") {
        frame.style.height = Math.max(data.height, MIN_HEIGHT) + "px"
      } else if (data.type === "ready" && options.onReady) {
        options.onReady()
      } else if (data.type === "started" && options.onStart) {
        options.onStart()
      } else if (data.type === "finished" && options.onFinish) {
        options.onFinish({ candidateId: data.candidateId })
      }
    }

    window.addEventListener("message", listen)
    element.appendChild(frame)

    return {
      destroy: function () {
        window.removeEventListener("message", listen)
        frame.remove()
      },
    }
  }

  window.Prepza = { embed: embed }
})()
