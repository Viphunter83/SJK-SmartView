import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";

// Firebase конфигурация через env vars (безопасно для клиентской стороны)
// Значения хранятся в .env.local (фронтенд) — не в git
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyB5EGsIkVk_vzutZvVz58IQb2PD-XYiZpY",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "sjk-smartview.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "sjk-smartview",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "sjk-smartview.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "747067032501",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:747067032501:web:7f22502b7cb7ca044f8ffc",
};

// Singleton инициализация
const firebaseApp = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const storage = getStorage(firebaseApp);

export { firebaseApp, auth, storage };
