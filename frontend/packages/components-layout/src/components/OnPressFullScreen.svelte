<script lang="ts">
	import CanvasSizeRectangle from './CanvasSizeRectangle.svelte';

	type Props = {
		onpress: () => void;
	};

	const props: Props = $props();

	// a press must BEGIN on this catcher to count — firing on a bare pointerup let a
	// click already in flight dismiss an overlay that mounted mid-click
	let armed = false;
</script>

<CanvasSizeRectangle
	onpointerdown={() => (armed = true)}
	onpointerup={() => {
		if (!armed) return;
		armed = false;
		props.onpress();
	}}
	cursor="pointer"
	eventMode="static"
	backgroundColor={0xffffff}
	backgroundAlpha={0.001}
/>
