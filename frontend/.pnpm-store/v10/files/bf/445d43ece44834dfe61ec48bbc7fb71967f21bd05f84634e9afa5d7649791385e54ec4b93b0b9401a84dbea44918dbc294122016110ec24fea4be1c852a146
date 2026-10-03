import * as routeModule from '__SENTRY_WRAPPING_TARGET_FILE__';
export * from '__SENTRY_WRAPPING_TARGET_FILE__';
import * as Sentry from '@sentry/nextjs';

const userPageModule = routeModule;
const pageComponent = userPageModule ? userPageModule.default : void 0;
const origGetInitialProps = pageComponent ? pageComponent.getInitialProps : void 0;
const origGetStaticProps = userPageModule ? userPageModule.getStaticProps : void 0;
const origGetServerSideProps = userPageModule ? userPageModule.getServerSideProps : void 0;
const getInitialPropsWrappers = Object.freeze({
  "/_app": Sentry.wrapAppGetInitialPropsWithSentry,
  "/_document": Sentry.wrapDocumentGetInitialPropsWithSentry,
  "/_error": Sentry.wrapErrorGetInitialPropsWithSentry
});
const getInitialPropsWrapper = getInitialPropsWrappers["__ROUTE__"] || Sentry.wrapGetInitialPropsWithSentry;
if (pageComponent && typeof origGetInitialProps === "function") {
  pageComponent.getInitialProps = getInitialPropsWrapper(origGetInitialProps);
}
const getStaticProps = typeof origGetStaticProps === "function" ? Sentry.wrapGetStaticPropsWithSentry(origGetStaticProps, "__ROUTE__") : void 0;
const getServerSideProps = typeof origGetServerSideProps === "function" ? Sentry.wrapGetServerSidePropsWithSentry(origGetServerSideProps, "__ROUTE__") : void 0;
const pageWrapperTemplate = pageComponent ? Sentry.wrapPageComponentWithSentry(pageComponent) : pageComponent;

export { pageWrapperTemplate as default, getServerSideProps, getStaticProps };
