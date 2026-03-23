import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {FC} from 'react';
import {SceneIcon, type SceneIconName} from './SceneIcons';

interface FormulaCardProps {
	keyword: string;
	meaning: string;
	example?: string;
	/** Optional small mark before example text (e.g. wrong-example cross). */
	examplePrefix?: SceneIconName;
	icon?: SceneIconName;
	color?: string;
}

export const FormulaCard: FC<FormulaCardProps> = ({
	keyword,
	meaning,
	example,
	examplePrefix,
	icon = 'lightbulb',
	color = '#4facfe',
}) => {
	const frame = useCurrentFrame();

	const scale = interpolate(frame, [0, 20], [0.5, 1], {
		extrapolateRight: 'clamp',
	});

	const opacity = interpolate(frame, [0, 20], [0, 1], {
		extrapolateRight: 'clamp',
	});

	const contentOpacity = interpolate(frame, [20, 40], [0, 1], {
		extrapolateRight: 'clamp',
	});

	const exampleOpacity = interpolate(frame, [40, 60], [0, 1], {
		extrapolateRight: 'clamp',
	});

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`,
				justifyContent: 'center',
				alignItems: 'center',
				padding: 100,
			}}
		>
			<div
				style={{
					background: 'white',
					borderRadius: 30,
					padding: 80,
					width: '100%',
					maxWidth: 1500,
					boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
					transform: `scale(${scale})`,
					opacity,
				}}
			>
				<div style={{textAlign: 'center'}}>
					<div
						style={{
							marginBottom: 20,
							display: 'flex',
							justifyContent: 'center',
						}}
					>
						<SceneIcon name={icon} size={80} color={color} />
					</div>
					<h1
						style={{
							fontSize: 72,
							fontWeight: 'bold',
							margin: 0,
							color: '#333',
							marginBottom: 40,
						}}
					>
						{keyword}
					</h1>
					<div style={{opacity: contentOpacity}}>
						<div
							style={{
								fontSize: 36,
								color: '#666',
								lineHeight: 1.6,
								marginBottom: 40,
							}}
						>
							{meaning}
						</div>
						{example && (
							<div style={{opacity: exampleOpacity}}>
								<div
									style={{
										background: '#f0f0f0',
										padding: '30px 40px',
										borderRadius: 15,
										fontSize: 28,
										color: '#444',
										display: 'flex',
										alignItems: 'flex-start',
										gap: 12,
									}}
								>
									<SceneIcon name="chat" size={36} color="#666" />
									<div style={{flex: 1}}>
										<strong>示例：</strong>
										<div
											style={{
												marginTop: 8,
												display: 'flex',
												alignItems: 'flex-start',
												gap: 10,
											}}
										>
											{examplePrefix ? (
												<span style={{flexShrink: 0, marginTop: 4}}>
													<SceneIcon name={examplePrefix} size={28} color="#c62828" />
												</span>
											) : null}
											<span>{example}</span>
										</div>
									</div>
								</div>
							</div>
						)}
					</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};
