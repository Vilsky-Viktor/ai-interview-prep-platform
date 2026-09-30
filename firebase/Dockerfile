FROM node:24-alpine

RUN npm install --global firebase-tools

WORKDIR /firebase

COPY firebase.json .firebaserc ./

EXPOSE 9199 4100

CMD ["firebase", "emulators:start", "--only", "auth", "--project", "demo-prepza"]
