import { describe, expect, test } from 'bun:test'
import * as THREE from 'three'
import { boxesOverlap } from './collision.js'
import { findAssetInstancePrefix } from './catalog-utils.js'

describe('hospital placement collision', () => {
  test('detects intersecting boxes', () => {
    const a = new THREE.Box3(new THREE.Vector3(0, 0, 0), new THREE.Vector3(2, 1, 2))
    const b = new THREE.Box3(new THREE.Vector3(1, 0, 1), new THREE.Vector3(3, 1, 3))
    expect(boxesOverlap(a, b)).toBe(true)
  })

  test('allows boxes that only touch at an edge', () => {
    const a = new THREE.Box3(new THREE.Vector3(0, 0, 0), new THREE.Vector3(1, 1, 1))
    const b = new THREE.Box3(new THREE.Vector3(1, 0, 0), new THREE.Vector3(2, 1, 1))
    expect(boxesOverlap(a, b)).toBe(false)
  })
})

describe('hospital asset extraction', () => {
  test('selects one numbered instance from a repeated room asset', () => {
    const names = [
      '044-adjustable-ward-bed0',
      '044-adjustable-ward-bed_head-section',
      '051-adjustable-ward-bed0'
    ]
    expect(findAssetInstancePrefix(names, 'adjustable-ward-bed')).toBe('044')
  })
})
