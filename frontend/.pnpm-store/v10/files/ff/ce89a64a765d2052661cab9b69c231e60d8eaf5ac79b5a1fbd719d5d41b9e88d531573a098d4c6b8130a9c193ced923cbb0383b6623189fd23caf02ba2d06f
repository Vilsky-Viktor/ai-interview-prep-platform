Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');

function wrapApiHandlerWithSentryVercelCrons(handler, vercelCronsConfig) {
  return new Proxy(handler, {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apply: (originalFunction, thisArg, args) => {
      if (!args?.[0]) {
        return originalFunction.apply(thisArg, args);
      }
      const [req] = args;
      let maybePromiseResult;
      const cronsKey = "nextUrl" in req ? req.nextUrl.pathname : req.url;
      const userAgentHeader = "nextUrl" in req ? req.headers.get("user-agent") : req.headers["user-agent"];
      if (!vercelCronsConfig || // do nothing if vercel crons config is missing
      !userAgentHeader?.includes("vercel-cron")) {
        return originalFunction.apply(thisArg, args);
      }
      const vercelCron = vercelCronsConfig.find((vercelCron2) => vercelCron2.path === cronsKey);
      if (!vercelCron?.path || !vercelCron.schedule) {
        return originalFunction.apply(thisArg, args);
      }
      const monitorSlug = vercelCron.path;
      const checkInId = core.captureCheckIn(
        {
          monitorSlug,
          status: "in_progress"
        },
        {
          maxRuntime: 60 * 12,
          // (minutes) so 12 hours - just a very high arbitrary number since we don't know the actual duration of the users cron job
          schedule: {
            type: "crontab",
            value: vercelCron.schedule
          }
        }
      );
      const startTime = core._INTERNAL_safeDateNow() / 1e3;
      const handleErrorCase = () => {
        core.captureCheckIn({
          checkInId,
          monitorSlug,
          status: "error",
          duration: core._INTERNAL_safeDateNow() / 1e3 - startTime
        });
      };
      try {
        maybePromiseResult = originalFunction.apply(thisArg, args);
      } catch (e) {
        handleErrorCase();
        throw e;
      }
      if (core.isObjectLike(maybePromiseResult) && "then" in maybePromiseResult) {
        Promise.resolve(maybePromiseResult).then(
          () => {
            core.captureCheckIn({
              checkInId,
              monitorSlug,
              status: "ok",
              duration: core._INTERNAL_safeDateNow() / 1e3 - startTime
            });
          },
          () => {
            handleErrorCase();
          }
        );
        return maybePromiseResult;
      } else {
        core.captureCheckIn({
          checkInId,
          monitorSlug,
          status: "ok",
          duration: core._INTERNAL_safeDateNow() / 1e3 - startTime
        });
        return maybePromiseResult;
      }
    }
  });
}

exports.wrapApiHandlerWithSentryVercelCrons = wrapApiHandlerWithSentryVercelCrons;
//# sourceMappingURL=wrapApiHandlerWithSentryVercelCrons.js.map
