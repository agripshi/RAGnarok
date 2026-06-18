import { createDarkTheme, type BrandVariants, type Theme } from '@fluentui/react-components';

/** Engineering brand purple ramp — anchored at #A100FF */
const engineeringBrand: BrandVariants = {
  10: '#14001f',
  20: '#240033',
  30: '#35004d',
  40: '#4a0066',
  50: '#5c0080',
  60: '#7300a3',
  70: '#8700c2',
  80: '#a100ff',
  90: '#b533ff',
  100: '#c966ff',
  110: '#db99ff',
  120: '#edccff',
  130: '#f5e0ff',
  140: '#f9edff',
  150: '#fcf5ff',
  160: '#ffffff',
};

const base = createDarkTheme(engineeringBrand);

export const engineeringTheme: Theme = {
  ...base,
  colorNeutralBackground1: '#000000',
  colorNeutralBackground2: '#0a0a0a',
  colorNeutralBackground3: '#141414',
  colorNeutralForeground1: '#ffffff',
  colorNeutralForeground2: '#e8e8e8',
  colorNeutralForeground3: '#b3b3b3',
  colorNeutralStroke1: 'rgba(255, 255, 255, 0.14)',
  colorNeutralStroke2: 'rgba(161, 0, 255, 0.35)',
};
