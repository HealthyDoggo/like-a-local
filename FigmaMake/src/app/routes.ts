import { createBrowserRouter } from 'react-router';
import { SplashScreen } from '@/app/screens/SplashScreen';
import { IntentScreen } from '@/app/screens/IntentScreen';
import { SelectCountryScreen } from '@/app/screens/SelectCountryScreen';
import { SelectCityScreen } from '@/app/screens/SelectCityScreen';
import { AddTipsScreen } from '@/app/screens/AddTipsScreen';
import { HomeScreen } from '@/app/screens/HomeScreen';
import { VisitCountryScreen } from '@/app/screens/VisitCountryScreen';
import { VisitCityScreen } from '@/app/screens/VisitCityScreen';
import { CityOverviewScreen } from '@/app/screens/CityOverviewScreen';
import { TipsListScreen } from '@/app/screens/TipsListScreen';
import { SavedScreen } from '@/app/screens/SavedScreen';
import { ContributeScreen } from '@/app/screens/ContributeScreen';
import { ProfileScreen } from '@/app/screens/ProfileScreen';
import { SettingsScreen } from '@/app/screens/SettingsScreen';
import { LanguageSettingsScreen } from '@/app/screens/LanguageSettingsScreen';
import { SignInScreen } from '@/app/screens/SignInScreen';
import { SignUpScreen } from '@/app/screens/SignUpScreen';
import { EmailSignInScreen } from '@/app/screens/EmailSignInScreen';
import { EmailSignUpScreen } from '@/app/screens/EmailSignUpScreen';
import { NotFoundScreen } from '@/app/screens/NotFoundScreen';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: SplashScreen,
  },
  {
    path: '/intent',
    Component: IntentScreen,
  },
  {
    path: '/sign-in',
    Component: SignInScreen,
  },
  {
    path: '/sign-in/email',
    Component: EmailSignInScreen,
  },
  {
    path: '/sign-up',
    Component: SignUpScreen,
  },
  {
    path: '/sign-up/email',
    Component: EmailSignUpScreen,
  },
  {
    path: '/onboarding/country',
    Component: SelectCountryScreen,
  },
  {
    path: '/onboarding/city',
    Component: SelectCityScreen,
  },
  {
    path: '/onboarding/contribute-country',
    Component: SelectCountryScreen,
  },
  {
    path: '/onboarding/tips',
    Component: AddTipsScreen,
  },
  {
    path: '/home',
    Component: HomeScreen,
  },
  {
    path: '/visit',
    Component: VisitCountryScreen,
  },
  {
    path: '/visit/city',
    Component: VisitCityScreen,
  },
  {
    path: '/city-overview',
    Component: CityOverviewScreen,
  },
  {
    path: '/tips',
    Component: TipsListScreen,
  },
  {
    path: '/saved',
    Component: SavedScreen,
  },
  {
    path: '/contribute',
    Component: ContributeScreen,
  },
  {
    path: '/profile',
    Component: ProfileScreen,
  },
  {
    path: '/settings',
    Component: SettingsScreen,
  },
  {
    path: '/settings/language',
    Component: LanguageSettingsScreen,
  },
  {
    path: '*',
    Component: NotFoundScreen,
  },
]);