import {Composition} from 'remotion';
import {PitchSlide} from './Pitch';
export const RemotionRoot=()=> <>
 <Composition id="Opening" component={PitchSlide} width={1280} height={720} fps={24} durationInFrames={72} defaultProps={{slide:0}}/>
 <Composition id="Threshold" component={PitchSlide} width={1280} height={720} fps={24} durationInFrames={72} defaultProps={{slide:1}}/>
 <Composition id="Method" component={PitchSlide} width={1280} height={720} fps={24} durationInFrames={72} defaultProps={{slide:2}}/>
 <Composition id="Demo" component={PitchSlide} width={1280} height={720} fps={24} durationInFrames={960} defaultProps={{slide:3}}/>
 <Composition id="Scope" component={PitchSlide} width={1280} height={720} fps={24} durationInFrames={72} defaultProps={{slide:4}}/>
 <Composition id="Closing" component={PitchSlide} width={1280} height={720} fps={24} durationInFrames={72} defaultProps={{slide:5}}/>
</>;
