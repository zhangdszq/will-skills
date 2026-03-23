import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {FC} from 'react';
import {SceneIcon, type SceneIconName} from './SceneIcons';

interface ChapterTitleProps {
	chapterNumber: string;
	title: string;
	description?: string;
	icon?: SceneIconName;
}

export const ChapterTitle: FC<ChapterTitleProps> = ({
	chapterNumber,
	title,
	description,
	icon = 'book',
}) => {
	const frame = useCurrentFrame();

	const slideIn = interpolate(frame, [0, 20], [-1920, 0], {
		extrapolateRight: 'clamp',
	});

	const opacity = interpolate(frame, [0, 20], [0, 1], {
		extrapolateRight: 'clamp',
	});

	const descriptionOpacity = interpolate(frame, [20, 40], [0, 1], {
		extrapolateRight: 'clamp',
	});

	return (
		<AbsoluteFill
			style={{
				background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
				justifyContent: 'center',
				alignItems: 'center',
			}}
		>
			<div
				style={{
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					textAlign: 'center',
					color: 'white',
					transform: `translateX(${slideIn}px)`,
					opacity,
				}}
			>
				<div
					style={{
						marginBottom: 20,
						color: 'white',
					}}
				>
					<SceneIcon name={icon} size={100} color="white" />
				</div>
				<div
					style={{
						fontSize: 36,
						fontWeight: 300,
						opacity: 0.9,
						marginBottom: 10,
					}}
				>
					{chapterNumber}
				</div>
				<h1
					style={{
						fontSize: 80,
						fontWeight: 'bold',
						margin: 0,
						textShadow: '3px 3px 6px rgba(0,0,0,0.2)',
					}}
				>
					{title}
				</h1>
				{description && (
					<p
						style={{
							fontSize: 32,
							marginTop: 30,
							opacity: descriptionOpacity,
							fontWeight: 300,
							maxWidth: 1200,
						}}
					>
						{description}
					</p>
				)}
			</div>
		</AbsoluteFill>
	);
};
