import { captureCheckIn, _INTERNAL_safeDateNow, isObjectLike } from '@sentry/core';

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
      const checkInId = captureCheckIn(
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
      const startTime = _INTERNAL_safeDateNow() / 1e3;
      const handleErrorCase = () => {
        captureCheckIn({
          checkInId,
          monitorSlug,
          status: "error",
          duration: _INTERNAL_safeDateNow() / 1e3 - startTime
        });
      };
      try {
        maybePromiseResult = originalFunction.apply(thisArg, args);
      } catch (e) {
        handleErrorCase();
        throw e;
      }
      if (isObjectLike(maybePromiseResult) && "then" in maybePromiseResult) {
        Promise.resolve(maybePromiseResult).then(
          () => {
            captureCheckIn({
              checkInId,
              monitorSlug,
              status: "ok",
              duration: _INTERNAL_safeDateNow() / 1e3 - startTime
            });
          },
          () => {
            handleErrorCase();
          }
        );
        return maybePromiseResult;
      } else {
        captureCheckIn({
          checkInId,
          monitorSlug,
          status: "ok",
          duration: _INTERNAL_safeDateNow() / 1e3 - startTime
        });
        return maybePromiseResult;
      }
    }
  });
}

export { wrapApiHandlerWithSentryVercelCrons };
//# sourceMappingURL=wrapApiHandlerWithSentryVercelCrons.js.map
