<script setup lang="ts">
import { OWGames, OWGamesEvents } from '@overwolf/overwolf-api-ts'
import { kGamesFeatures } from '@/consts'
import { onMounted, ref } from 'vue'



function useInGameTracker() {

    const events = ref<Array<{ timestamp: string, data: any }>>([])
    const infos = ref<Array<{ timestamp: string, data: any }>>([])
    const gameInfo = ref<any>(null)
    let gameEventsListener: OWGamesEvents

    const timestamped = (data: any) => ({
        timestamp: new Date().toISOString(),
        data
    })

    const onInfoUpdates = (info: any) => {
        if (info.match_info?.game_type) {
            gameInfo.value = info.match_info
        }
        infos.value.push(timestamped(info))
    }

    const onNewEvents = async (e: any) => {
        events.value.push(timestamped(e))

        const matchEnded = e.events.some(
            (event: any) => event.name === 'match_end'
        )

        if (matchEnded) {
            if (!gameInfo.value || gameInfo.value.game_type !== 'RANKED') {
                console.log(`Match ended but not ranked: ${JSON.stringify(gameInfo.value)}. Skipping save/send.`)
                events.value = []
                infos.value = []
                return
            }
            const payload = {
                events: [...events.value],
                infos: [...infos.value]
            }

            try {
                const response = await fetch('https://ow.yda.ng/match', {
                    method: 'POST',
                    body: JSON.stringify(payload),
                    headers: {
                        'Content-Type': 'application/json',
                        'x-secret': 'placeholder'
                    }
                })

                if (response.ok) {
                    console.log('Match data sent successfully.')
                } else {
                    console.error('Failed to send match data:', await response.text())
                }
            } catch (error) {
                console.error('Error sending match data:', error)
            } finally {
                events.value = []
                infos.value = []
            }
        }
    }

    const startListening = async () => {
        const info = await OWGames.getRunningGameInfo()
        const gameClassId = info?.isRunning ? info.classId : null
        const features = kGamesFeatures.get(gameClassId || 0)
        if (!features?.length) return

        gameEventsListener = new OWGamesEvents(
            { onInfoUpdates, onNewEvents },
            features
        )

        gameEventsListener.start()
        gameEventsListener.getInfo()
    }

    return { startListening }
}



const tracker = useInGameTracker()
onMounted(() => {
    tracker.startListening()
})
</script>
