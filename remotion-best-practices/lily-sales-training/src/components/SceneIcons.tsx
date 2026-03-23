import React, {FC} from 'react';

/** Named scene icons — all drawn as inline SVG (no emoji fonts). */
export type SceneIconName =
	| 'book'
	| 'trophy'
	| 'phone'
	| 'stethoscope'
	| 'diamond'
	| 'target'
	| 'burger'
	| 'shield'
	| 'soccer'
	| 'lightbulb'
	| 'person'
	| 'briefcase'
	| 'star'
	| 'chat'
	| 'cross';

const svgWrap = (
	children: React.ReactNode,
	size: number,
	viewBox: string,
	color = 'currentColor'
) => (
	<svg
		width={size}
		height={size}
		viewBox={viewBox}
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		aria-hidden
		style={{display: 'block', color}}
	>
		{children}
	</svg>
);

export const SceneIcon: FC<{
	name: SceneIconName;
	size?: number;
	color?: string;
}> = ({name, size = 96, color}) => {
	switch (name) {
		case 'book':
			return svgWrap(
				<>
					<rect x="8" y="6" width="36" height="44" rx="3" stroke={color} strokeWidth="3" />
					<rect x="22" y="6" width="36" height="44" rx="3" stroke={color} strokeWidth="3" />
					<path d="M14 18h18M14 26h18M36 18h14" stroke={color} strokeWidth="2" />
				</>,
				size,
				'0 0 64 56',
				color
			);
		case 'trophy':
			return svgWrap(
				<>
					<path
						d="M20 8h24v6c0 12-6 20-12 22v6h-8v-6c-6-2-12-10-12-22V8z"
						stroke={color}
						strokeWidth="3"
					/>
					<path d="M16 14H8v4c0 8 4 12 10 12M48 14h8v4c0 8-4 12-10 12" stroke={color} strokeWidth="3" />
					<path d="M24 52h16" stroke={color} strokeWidth="4" strokeLinecap="round" />
					<path d="M20 56h24" stroke={color} strokeWidth="3" strokeLinecap="round" />
				</>,
				size,
				'0 0 64 64',
				color
			);
		case 'phone':
			return svgWrap(
				<>
					<rect x="18" y="6" width="28" height="52" rx="6" stroke={color} strokeWidth="3" />
					<path d="M26 14h12M28 48h8" stroke={color} strokeWidth="3" strokeLinecap="round" />
				</>,
				size,
				'0 0 64 64',
				color
			);
		case 'stethoscope':
			return svgWrap(
				<>
					<path
						d="M12 20c0-6 4-10 10-10s10 4 10 10v14c0 6-4 10-10 10S12 40 12 34V20z"
						stroke={color}
						strokeWidth="3"
					/>
					<path d="M32 24h10c6 0 10 4 10 10v6c0 6-4 10-10 10s-10-4-10-10"
						stroke={color}
						strokeWidth="3"
					/>
					<circle cx="46" cy="48" r="6" stroke={color} strokeWidth="3" />
				</>,
				size,
				'0 0 64 64',
				color
			);
		case 'diamond':
			return svgWrap(
				<path d="M32 6L52 32 32 58 12 32 32 6z" stroke={color} strokeWidth="3" />,
				size,
				'0 0 64 64',
				color
			);
		case 'target':
			return svgWrap(
				<>
					<circle cx="32" cy="32" r="26" stroke={color} strokeWidth="3" />
					<circle cx="32" cy="32" r="16" stroke={color} strokeWidth="3" />
					<circle cx="32" cy="32" r="6" fill={color} />
				</>,
				size,
				'0 0 64 64',
				color
			);
		case 'burger':
			return svgWrap(
				<>
					<path d="M8 18h48v8H8z" fill={color} opacity="0.35" />
					<rect x="6" y="28" width="52" height="10" rx="3" stroke={color} strokeWidth="3" />
					<rect x="6" y="42" width="52" height="10" rx="3" stroke={color} strokeWidth="3" />
					<path d="M10 56h44" stroke={color} strokeWidth="4" strokeLinecap="round" />
				</>,
				size,
				'0 0 64 64',
				color
			);
		case 'shield':
			return svgWrap(
				<path
					d="M32 6 L52 14 V34C52 48 32 58 32 58S12 48 12 34V14L32 6z"
					stroke={color}
					strokeWidth="3"
				/>,
				size,
				'0 0 64 64',
				color
			);
		case 'soccer':
			return svgWrap(
				<>
					<circle cx="32" cy="32" r="24" stroke={color} strokeWidth="3" />
					<path
						d="M32 14l8 8-3 10h-10l-3-10 8-8zM20 36l6 4 2 10M44 36l-6 4-2 10"
						stroke={color}
						strokeWidth="2"
					/>
				</>,
				size,
				'0 0 64 64',
				color
			);
		case 'lightbulb':
			return svgWrap(
				<>
					<path
						d="M32 8c10 0 18 8 18 18 0 8-6 14-8 18H22c-2-4-8-10-8-18 0-10 8-18 18-18z"
						stroke={color}
						strokeWidth="3"
					/>
					<path d="M24 48h16M26 54h12" stroke={color} strokeWidth="3" strokeLinecap="round" />
				</>,
				size,
				'0 0 64 64',
				color
			);
		case 'person':
			return svgWrap(
				<>
					<circle cx="24" cy="14" r="8" stroke={color} strokeWidth="2.5" />
					<path d="M10 40c2-10 10-14 14-14s12 4 14 14" stroke={color} strokeWidth="2.5" />
				</>,
				size,
				'0 0 48 44',
				color
			);
		case 'briefcase':
			return svgWrap(
				<>
					<rect x="8" y="16" width="40" height="30" rx="4" stroke={color} strokeWidth="2.5" />
					<path d="M22 16V12a4 4 0 014-4h4a4 4 0 014 4v4" stroke={color} strokeWidth="2.5" />
					<path d="M8 28h40" stroke={color} strokeWidth="2" />
				</>,
				size,
				'0 0 56 48',
				color
			);
		case 'star':
			return svgWrap(
				<path
					d="M32 6l7.2 18.5L58 26l-15 13 5.7 18.5L32 44l-16.7 13.5L21 39 6 26l18.8-1.5L32 6z"
					stroke={color}
					strokeWidth="2.5"
				/>,
				size,
				'0 0 64 64',
				color
			);
		case 'chat':
			return svgWrap(
				<>
					<path
						d="M6 8h44a4 4 0 014 4v22a4 4 0 01-4 4H28l-10 10v-10H10a4 4 0 01-4-4V12a4 4 0 014-4z"
						stroke={color}
						strokeWidth="2.5"
					/>
					<path d="M16 22h28M16 30h18" stroke={color} strokeWidth="2" />
				</>,
				size,
				'0 0 56 48',
				color
			);
		case 'cross':
			return svgWrap(
				<path d="M10 10l28 28M38 10L10 38" stroke={color} strokeWidth="3.5" strokeLinecap="round" />,
				size,
				'0 0 48 48',
				color
			);
		default:
			return null;
	}
};

/** Inline row: icon + label for dialogue headers */
export const IconLabel: FC<{
	icon: SceneIconName;
	label: string;
	iconSize?: number;
	style?: React.CSSProperties;
}> = ({icon, label, iconSize = 28, style}) => (
	<div
		style={{
			display: 'flex',
			alignItems: 'center',
			gap: 10,
			...style,
		}}
	>
		<SceneIcon name={icon} size={iconSize} color="#999" />
		<span>{label}</span>
	</div>
);
