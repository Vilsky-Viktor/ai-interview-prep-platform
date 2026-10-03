Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const reactRouter = require('react-router');
const reactrouter_compat = require('./reactrouter.compat.js');

function reactRouterBrowserTracingIntegration(options = {}) {
  return reactrouter_compat.reactRouterBrowserTracingIntegration({
    useLocation: reactRouter.useLocation,
    useNavigationType: reactRouter.useNavigationType,
    createRoutesFromChildren: reactRouter.createRoutesFromChildren,
    matchRoutes: reactRouter.matchRoutes,
    ...options
  });
}

exports.wrapCreateBrowserRouter = reactrouter_compat.wrapCreateBrowserRouter;
exports.wrapCreateMemoryRouter = reactrouter_compat.wrapCreateMemoryRouter;
exports.wrapReactRouterRouting = reactrouter_compat.wrapReactRouterRouting;
exports.wrapUseRoutes = reactrouter_compat.wrapUseRoutes;
exports.reactRouterBrowserTracingIntegration = reactRouterBrowserTracingIntegration;
//# sourceMappingURL=react-router.js.map
